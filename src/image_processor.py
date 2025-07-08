import wx
import os
import random
import uuid

def generate_images(parent, source_data, generate_settings):
    # 1. Validation
    # Check for missing files
    missing_files = []
    for group in source_data['paths']:
        for path in group:
            if not path or not os.path.exists(path):
                missing_files.append(path if path else "Empty path")
    if missing_files:
        wx.MessageBox(f"The following source files are missing or not specified:\n\n" +
                      "\n".join(missing_files), "Missing Files", wx.OK | wx.ICON_ERROR)
        return

    # Check image sizes within groups
    for i, group in enumerate(source_data['paths']):
        first_image = wx.Image(group[0], wx.BITMAP_TYPE_ANY)
        if not first_image.IsOk():
            wx.MessageBox(f"Could not load image: {group[0]}", "Error", wx.OK | wx.ICON_ERROR)
            return
        size = first_image.GetSize()
        for path in group[1:]:
            image = wx.Image(path, wx.BITMAP_TYPE_ANY)
            if not image.IsOk():
                wx.MessageBox(f"Could not load image: {path}", "Error", wx.OK | wx.ICON_ERROR)
                return
            if image.GetSize() != size:
                wx.MessageBox(f"Images in group {i+1} do not have the same dimensions.",
                              "Dimension Mismatch", wx.OK | wx.ICON_ERROR)
                return

    # Check if tile size is smaller than source
    first_image = wx.Image(source_data['paths'][0][0], wx.BITMAP_TYPE_ANY)
    source_size = first_image.GetSize()
    tile_size = (generate_settings['width'], generate_settings['height'])
    if tile_size[0] >= source_size[0] or tile_size[1] >= source_size[1]:
        wx.MessageBox("Tile dimensions must be smaller than the source image dimensions.",
                      "Invalid Tile Size", wx.OK | wx.ICON_ERROR)
        return

    # Pre-load all source images into memory for performance
    progress_dialog = wx.ProgressDialog(
        "Loading Images",
        "Loading source images...",
        maximum=len(source_data['paths']) * len(source_data['paths'][0]) + generate_settings['tiles'],
        parent=parent,
        style=wx.PD_APP_MODAL | wx.PD_AUTO_HIDE | wx.PD_CAN_ABORT
    )
    
    loaded_images = []
    load_progress = 0
    for group_index, group_paths in enumerate(source_data['paths']):
        group_images = []
        for set_index, path in enumerate(group_paths):
            keep_going, _ = progress_dialog.Update(load_progress, f"Loading image {load_progress + 1}...")
            if not keep_going:
                progress_dialog.Destroy()
                wx.MessageBox("Image loading was cancelled.", "Cancelled", wx.OK | wx.ICON_WARNING)
                return
            
            image = wx.Image(path, wx.BITMAP_TYPE_ANY)
            if not image.IsOk():
                progress_dialog.Destroy()
                wx.MessageBox(f"Could not load image: {path}", "Error", wx.OK | wx.ICON_ERROR)
                return
            group_images.append(image)
            load_progress += 1
        loaded_images.append(group_images)

    # 2. Generation Process
    num_tiles = generate_settings['tiles']
    
    cancelled = False
    for i in range(num_tiles):
        keep_going, _ = progress_dialog.Update(load_progress + i, f"Processing tile {i+1} of {num_tiles}...")
        if not keep_going:
            cancelled = True
            break

        unique_id = uuid.uuid4().hex[:8]
        for group_index, group_images in enumerate(loaded_images):
            # Determine transformations for this tile
            do_rotate = generate_settings['rotate'] and random.randint(1, 100) <= generate_settings['rotate_value']
            do_flip = generate_settings['flip'] and random.randint(1, 100) <= generate_settings['flip_value']
            use_bigger = generate_settings['use_bigger_regions'] and random.randint(1, 100) <= generate_settings['bigger_regions_value']

            # Get dimensions from the first image in the group
            source_width, source_height = group_images[0].GetSize()
            tile_width, tile_height = generate_settings['width'], generate_settings['height']
            
            # Define random region
            if use_bigger:
                # Randomly increase the size of the region, maintaining aspect ratio
                max_scale_x = source_width / tile_width
                max_scale_y = source_height / tile_height
                scale = random.uniform(1.0, min(max_scale_x, max_scale_y))
                region_width = int(tile_width * scale)
                region_height = int(tile_height * scale)
            else:
                region_width, region_height = tile_width, tile_height

            rand_x = random.randint(0, source_width - region_width)
            rand_y = random.randint(0, source_height - region_height)
            region = wx.Rect(rand_x, rand_y, region_width, region_height)

            for set_index, source_image in enumerate(group_images):
                # Work with a copy of the loaded image
                tile_image = source_image.GetSubImage(region)

                if use_bigger:
                    tile_image.Rescale(tile_width, tile_height, wx.IMAGE_QUALITY_HIGH)

                # Apply transformations
                if do_flip:
                    if random.choice([True, False]):
                        tile_image = tile_image.Mirror(horizontally=True)
                    else:
                        tile_image = tile_image.Mirror(horizontally=False)

                if do_rotate:
                    if tile_width == tile_height:
                        rotation = random.choice([90, 180, 270])
                        if rotation == 90:
                            tile_image = tile_image.Rotate90(clockwise=True)
                        elif rotation == 180:
                            tile_image = tile_image.Rotate180()
                        elif rotation == 270:
                            tile_image = tile_image.Rotate90(clockwise=False)
                    else: # Can only rotate 180 for non-square
                        tile_image = tile_image.Rotate180()

                # Save the file
                set_name = source_data['set_names'][set_index]
                output_dir = os.path.join(generate_settings['output_path'], set_name)
                os.makedirs(output_dir, exist_ok=True)

                filename = (f"{generate_settings['export_prefix']}"
                            f"{group_index + 1}_{i + 1}."
                            f"{generate_settings['image_type']}")
                
                output_path = os.path.join(output_dir, filename)
                
                image_type = generate_settings['image_type'].lower()
                if image_type == 'jpg':
                    image_type = wx.BITMAP_TYPE_JPEG
                elif image_type == 'bmp':
                    image_type = wx.BITMAP_TYPE_BMP
                else:
                    image_type = wx.BITMAP_TYPE_PNG

                tile_image.SaveFile(output_path, image_type)

    progress_dialog.Destroy()
    if cancelled:
        wx.MessageBox("Image generation was cancelled. Some images may have been generated.", "Cancelled", wx.OK | wx.ICON_WARNING)
    else:
        wx.MessageBox("Image generation complete!", "Success", wx.OK | wx.ICON_INFORMATION)
