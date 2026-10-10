"""Run the published DualTrack model (ImFusion, CC BY-NC-SA 4.0) on TUS-REC sweeps; save predicted probe poses.

Runs in the separate environment .venv-dualtrack with the repo cloned at third_party/DualTrack and checkpoints in
third_party/weights. Preprocessing follows the authors' evaluation configs exactly:
  2024 model (dualtrack_final.pt): global = full frame resized to 224, /255, normalise mean 0.5 std 0.25;
                                   local = centre crop 256x256, /255
  2025 model (ft_tus_rec_2025):    global = crop 50 px each side, resize 224 (skimage), /255, mean 0 std 1;
                                   local = centre crop 256x256, /255
Output per scan: <out>/<scan>.npz with pred_tforms [N,4,4] (tool->world, anchored to the true first pose) and
gt_tforms, so the coverage engine can use them as a pose source unchanged.

Usage: .venv-dualtrack/Scripts/python scripts/run_dualtrack.py --model 2024 --dataset data/extracted/tusrec2024_val --out outputs/dualtrack_2024
"""
import argparse
import os
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DT = ROOT / "third_party" / "DualTrack"
sys.path.insert(0, str(DT))
sys.path.insert(1, str(ROOT / "src"))

import torch  # noqa: E402
import h5py  # noqa: E402
from omegaconf import OmegaConf  # noqa: E402

MODELS = {
    "2024": dict(config=DT / "configs/model/dualtrack.yaml", ckpt=ROOT / "third_party/weights/dualtrack_final.pt",
                 g_mean=0.5, g_std=0.25, g_crop=0),
    "2025": dict(config=DT / "configs/model/dualtrack_ft_tus_rec_2025.yaml",
                 ckpt=ROOT / "third_party/weights/dualtrack_ft_tus_rec_2025_v3_best.pt",
                 g_mean=0.0, g_std=1.0, g_crop=50),
}


def load_model(which, device):
    os.chdir(DT)  # some registry code resolves relative paths
    from src.models import get_model
    m = MODELS[which]
    cfg = OmegaConf.load(m["config"])
    cfg.checkpoint = str(m["ckpt"])
    model = get_model(**cfg)
    return model.to(device).eval()


def preprocess(frames, spec):
    import torch.nn.functional as F
    x = torch.from_numpy(frames).float()[:, None] / 255.0             # N,1,480,640
    if spec["g_crop"]:
        import skimage
        c = spec["g_crop"]
        g = np.stack([(skimage.transform.resize(f[c:-c, c:-c], (224, 224)) * 255).astype(np.uint8) for f in frames])
        g = torch.from_numpy(g).float()[:, None] / 255.0
    else:
        g = F.interpolate(x, size=(224, 224), mode="bilinear", antialias=True, align_corners=False)
    g = (g - spec["g_mean"]) / spec["g_std"]
    H, W = frames.shape[1:]
    r0, c0 = (H - 256) // 2, (W - 256) // 2
    loc = x[:, :, r0:r0 + 256, c0:c0 + 256]
    return g[None], loc[None]                                          # add batch dim


def converter():
    from scripts.data.convert_tus_rec_format_to_dualtrack_format import TUSRecToDualTrackConverter
    return TUSRecToDualTrackConverter.from_hardcoded_tus_rec_2024_calibration_settings()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", choices=["2024", "2025"], default="2024")
    ap.add_argument("--dataset", required=True)
    ap.add_argument("--scans", default="", help="comma list of scan names; default all")
    ap.add_argument("--max-scans", type=int, default=0)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    dataset = (ROOT / a.dataset).resolve() if not os.path.isabs(a.dataset) else Path(a.dataset)
    out = (ROOT / a.out).resolve() if not os.path.isabs(a.out) else Path(a.out)
    out.mkdir(parents=True, exist_ok=True)

    from uscov.data import index_dataset
    ds = index_dataset(dataset)
    names = a.scans.split(",") if a.scans else ds.names()
    if a.max_scans:
        names = names[:a.max_scans]

    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = load_model(a.model, device)
    from src.utils.pose import get_global_and_relative_pred_trackings_from_vectors
    conv = converter()
    A = conv.image_in_tus_rec_coords_to_tool @ conv.image_in_dualtrack_coords_to_image_in_tus_rec_coords
    A_inv = np.linalg.inv(A)
    spec = MODELS[a.model]

    for name in names:
        scan = ds.load(name)
        g, loc = preprocess(scan.frames, spec)
        t0 = time.time()
        with torch.no_grad(), torch.autocast(device_type="cuda", enabled=device == "cuda"):
            model.set_current_data_ids([name])
            model.local_encoder[0].input_mode = "images"
            pred = model(g.to(device), loc.to(device))
        dt = time.time() - t0
        vec = pred[0].float().cpu().numpy()                             # N-1 x 6 relative pose vectors
        glob, _ = get_global_and_relative_pred_trackings_from_vectors(vec)  # N x 4x4, image_dt(i) in image_dt(0)
        img_dt_world_gt = scan.tforms @ A                               # true image_dt -> world
        pred_img_world = img_dt_world_gt[0][None] @ glob.astype(np.float64)
        pred_tforms = pred_img_world @ A_inv                           # back to tool -> world
        np.savez_compressed(out / f"{name}.npz", pred_tforms=pred_tforms, gt_tforms=scan.tforms, rel_vectors=vec)
        # quick metric: centre-pixel drift
        p = np.array([(scan.shape[1] + 1) / 2, (scan.shape[0] + 1) / 2, 0, 1.0])
        T_gt = scan.frame_to_world(); T_pr = scan.frame_to_world(pred_tforms)
        e = np.linalg.norm((T_gt @ p)[:, :3] - (T_pr @ p)[:, :3], axis=1)
        path = np.linalg.norm(np.diff((T_gt @ p)[:, :3], axis=0), axis=1).sum()
        print(f"{name}: {scan.n_frames} frames, {dt:.2f} s, final drift {e[-1]:.1f} mm ({e[-1]/path*100:.1f}%), "
              f"mean err {e.mean():.1f} mm, path {path:.0f} mm", flush=True)
        torch.cuda.empty_cache()


if __name__ == "__main__":
    main()
