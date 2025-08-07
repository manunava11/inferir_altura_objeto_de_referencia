import os
print("Checkpoint existe:", os.path.exists("sam_vit_b_01ec64.pth"))

try:
    import segment_anything
    print("✅ segment_anything OK")
except Exception as e:
    print("❌ segment_anything:", e)

try:
    from segment_anything import sam_model_registry
    print("✅ sam_model_registry OK")
except Exception as e:
    print("❌ sam_model_registry:", e)

try:
    sam = sam_model_registry["vit_b"](checkpoint="sam_vit_b_01ec64.pth")
    print("✅ SAM model created")
except Exception as e:
    print("❌ SAM model error:", e)
