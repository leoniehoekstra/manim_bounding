from manim import *
import pandas as pd
import os

class SampleBoundingBoxes(Scene):
    def construct(self):
        # === Title ===
        title = Text("Ground Truth vs Predicted Labels", font_size=42, color=BLUE)
        title.to_edge(UP, buff=0.5)
        self.play(Write(title))

        # === Load CSV ===
        # Ensure this is the correct, cleaned CSV file.
        df = pd.read_csv("fixed.csv", dtype={'filename': str}).head(4)

        # === Colors ===
        GT_COLOR = "#89CFF0" # Baby Blue
        MATCH_COLOR = GREEN
        MISMATCH_COLOR = RED

        # === Image Display Scale Factor ===
        # Adjust this to control the size of displayed images and bounding boxes.
        IMAGE_DISPLAY_SCALE_FACTOR = 0.65 # You can experiment with this value

        # Lists to hold Mobjects for each image
        image_mobs = []
        true_texts_main = [] # Main "True: ..." labels
        pred_texts_main = [] # Main "Pred: ..." labels
        all_gt_box_groups_for_scene = [] # Groups of (box + box_label) for GT
        all_pred_box_groups_for_scene = [] # Groups of (box + box_label) for Pred

        for idx, row in df.iterrows():
            # Load and scale image
            img_path = os.path.join("fixed", str(row["filename"]))
            image = ImageMobject(img_path).scale(IMAGE_DISPLAY_SCALE_FACTOR)
            image_mobs.append(image) # Add image to list ONCE

            # --- Ground Truth Bounding Boxes and Labels ---
            current_gt_box_group = VGroup() # Group for all GT boxes & labels for THIS image
            if pd.notna(row["true_boxes"]) and str(row["true_boxes"]).lower() != "none" and str(row["true_boxes"]).strip() != "":
                gt_boxes_data = str(row["true_boxes"]).split(";")
                gt_labels_data = str(row["true_labels"]).split("|")
                for i, box_coords_str in enumerate(gt_boxes_data):
                    if not box_coords_str.strip(): continue
                    try:
                        x1, y1, x2, y2 = map(int, box_coords_str.split(","))
                    except ValueError:
                        print(f"Warning: Could not parse box coordinates '{box_coords_str}' for image {row['filename']}")
                        continue # Skip this box if coordinates are malformed
                        
                    w_orig, h_orig = x2 - x1, y2 - y1

                    if w_orig <= 0 or h_orig <= 0: continue # Skip zero or negative size boxes

                    w_scaled = w_orig * IMAGE_DISPLAY_SCALE_FACTOR
                    h_scaled = h_orig * IMAGE_DISPLAY_SCALE_FACTOR

                    rect = Rectangle(width=w_scaled, height=h_scaled, color=GT_COLOR, stroke_width=3) # Increased stroke_width for visibility

                    center_x_orig_pixels = x1 + w_orig / 2
                    center_y_orig_pixels = y1 + h_orig / 2
                    
                    rect.move_to(
                        image.get_corner(UP + LEFT) + 
                        RIGHT * center_x_orig_pixels * IMAGE_DISPLAY_SCALE_FACTOR + 
                        DOWN * center_y_orig_pixels * IMAGE_DISPLAY_SCALE_FACTOR
                    )
                    
                    label_str = gt_labels_data[i % len(gt_labels_data)]
                    box_label_text = Text(label_str, font_size=16, color=GT_COLOR).scale(IMAGE_DISPLAY_SCALE_FACTOR * 0.6)
                    box_label_text.next_to(rect.get_corner(UP + LEFT), UP, buff=0.03 * IMAGE_DISPLAY_SCALE_FACTOR)
                    current_gt_box_group.add(rect, box_label_text)
            all_gt_box_groups_for_scene.append(current_gt_box_group)

            # --- Predicted Bounding Boxes and Labels ---
            current_pred_box_group = VGroup() # Group for all Pred boxes & labels for THIS image
            if pd.notna(row["pred_boxes"]) and str(row["pred_boxes"]).lower() != "none" and str(row["pred_boxes"]).strip() != "":
                pred_boxes_data = str(row["pred_boxes"]).split(";")
                pred_labels_data = str(row["predicted_labels"]).split("|") if pd.notna(row["predicted_labels"]) and str(row["predicted_labels"]).lower() != "none" else []
                true_labels_list = str(row["true_labels"]).split("|") if pd.notna(row["true_labels"]) and str(row["true_labels"]).lower() != "none" else []

                for i, box_coords_str in enumerate(pred_boxes_data):
                    if not box_coords_str.strip(): continue
                    try:
                        x1, y1, x2, y2 = map(int, box_coords_str.split(","))
                    except ValueError:
                        print(f"Warning: Could not parse box coordinates '{box_coords_str}' for image {row['filename']}")
                        continue
                        
                    w_orig, h_orig = x2 - x1, y2 - y1

                    if w_orig <= 0 or h_orig <= 0: continue

                    w_scaled = w_orig * IMAGE_DISPLAY_SCALE_FACTOR
                    h_scaled = h_orig * IMAGE_DISPLAY_SCALE_FACTOR

                    label_str = pred_labels_data[i] if i < len(pred_labels_data) else "?"
                    color = MATCH_COLOR if label_str in true_labels_list else MISMATCH_COLOR
                    
                    rect = Rectangle(width=w_scaled, height=h_scaled, color=color, stroke_width=3) # Increased stroke_width

                    center_x_orig_pixels = x1 + w_orig / 2
                    center_y_orig_pixels = y1 + h_orig / 2
                    
                    rect.move_to(
                        image.get_corner(UP + LEFT) + 
                        RIGHT * center_x_orig_pixels * IMAGE_DISPLAY_SCALE_FACTOR + 
                        DOWN * center_y_orig_pixels * IMAGE_DISPLAY_SCALE_FACTOR
                    )
                    
                    box_label_text = Text(label_str, font_size=16, color=color).scale(IMAGE_DISPLAY_SCALE_FACTOR * 0.6)
                    box_label_text.next_to(rect.get_corner(UP + LEFT), UP, buff=0.03 * IMAGE_DISPLAY_SCALE_FACTOR)
                    current_pred_box_group.add(rect, box_label_text)
            all_pred_box_groups_for_scene.append(current_pred_box_group)

            # --- Main Texts under each image ---
            main_true_text = Text(f"True: {row['true_labels']}", font_size=18, color=GT_COLOR).scale(IMAGE_DISPLAY_SCALE_FACTOR * 0.9)
            main_pred_text = Text(f"Pred: {row['predicted_labels']}", font_size=18, color=WHITE).scale(IMAGE_DISPLAY_SCALE_FACTOR * 0.9)
            
            true_texts_main.append(main_true_text)
            pred_texts_main.append(main_pred_text)

        # --- Arrange elements on Scene ---
        # Arrange images horizontally
        image_group = Group(*image_mobs).arrange(RIGHT, buff=0.7).to_edge(UP, buff=1.2) # Use Group, adjust buff/to_edge

        # Position main labels under each corresponding arranged image
        for i in range(len(image_mobs)):
            if i < len(true_texts_main):
                true_texts_main[i].next_to(image_mobs[i], DOWN, buff=0.2 * IMAGE_DISPLAY_SCALE_FACTOR)
            if i < len(pred_texts_main) and i < len(true_texts_main): # Ensure true_texts_main[i] exists
                pred_texts_main[i].next_to(true_texts_main[i], DOWN, buff=0.15 * IMAGE_DISPLAY_SCALE_FACTOR)
        
        # These groups are for fading all texts together if needed, but individual fading is also used.
        all_main_true_texts_group = VGroup(*true_texts_main)
        all_main_pred_texts_group = VGroup(*pred_texts_main)
        
        # The box groups (all_gt_box_groups_for_scene, all_pred_box_groups_for_scene) are already lists of VGroups.
        # We will add them to the scene directly during animation.

        # === Animation ===
        self.play(FadeIn(image_group), run_time=2)
        self.wait(0.5)

        # Temporary VGroups for animating all current GT/Pred items together for each step
        current_gt_display_group = VGroup()
        current_pred_display_group = VGroup()

        # Show Ground Truth for all images
        for i in range(len(image_mobs)):
            # Add GT boxes for current image to scene (they are already positioned relative to image)
            # The all_gt_box_groups_for_scene[i] mobjects are positioned relative to their image.
            # We need to add them to the scene for Create to work on them.
            self.add(all_gt_box_groups_for_scene[i])
            # Add main true text for current image to scene
            if i < len(true_texts_main):
                self.add(true_texts_main[i]) # Add to scene before FadeIn if not already part of another displayed group

        # Animate GT items appearing
        # Create GT boxes and FadeIn main GT texts simultaneously for all images
        gt_anims = []
        for i in range(len(image_mobs)):
            if all_gt_box_groups_for_scene[i].submobjects: # If there are boxes
                gt_anims.append(Create(all_gt_box_groups_for_scene[i]))
            if i < len(true_texts_main):
                gt_anims.append(FadeIn(true_texts_main[i]))
        if gt_anims:
            self.play(*gt_anims, run_time=1.5)
        self.wait(2)

        # Fade out GT boxes and main GT texts, then Show Predictions
        fade_out_gt_anims = []
        create_pred_anims = []

        for i in range(len(image_mobs)):
            if all_gt_box_groups_for_scene[i].submobjects:
                fade_out_gt_anims.append(FadeOut(all_gt_box_groups_for_scene[i]))
            # Main GT texts are already handled by all_main_true_texts_group for collective fade if needed later,
            # or can be faded out individually if preferred. Here, let's assume they stay until the end with pred text.
            
            # Add Pred boxes for current image to scene
            self.add(all_pred_box_groups_for_scene[i])
            # Add main pred text for current image to scene
            if i < len(pred_texts_main):
                self.add(pred_texts_main[i])

            if all_pred_box_groups_for_scene[i].submobjects: # If there are boxes
                create_pred_anims.append(Create(all_pred_box_groups_for_scene[i]))
            if i < len(pred_texts_main):
                create_pred_anims.append(FadeIn(pred_texts_main[i]))
        
        if fade_out_gt_anims: # First, fade out all GT boxes
            self.play(*fade_out_gt_anims, run_time=0.5)
        if create_pred_anims: # Then, create all prediction boxes and fade in their texts
            self.play(*create_pred_anims, run_time=1.5)

        self.wait(3)
        
        # Fade out everything
        final_fade_out_mobjects = [image_group, title, all_main_true_texts_group, all_main_pred_texts_group]
        # Add individual prediction box groups to the list for fading out
        for group in all_pred_box_groups_for_scene:
            if group.submobjects:
                final_fade_out_mobjects.append(group)
        # Also, if GT texts weren't faded out with boxes, add them
        # For simplicity, all_main_true_texts_group covers this.

        mobjects_to_actually_fade = [m for m in final_fade_out_mobjects if m.submobjects or isinstance(m, Text)] # Filter for non-empty/drawable
        if mobjects_to_actually_fade:
            self.play(*[FadeOut(m) for m in mobjects_to_actually_fade])
