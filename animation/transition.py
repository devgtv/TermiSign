from animation.poses import POSES


def interpolate_poses(pose_a: str, pose_b: str, steps: int = 3) -> list[list[str]]:
    if pose_a not in POSES or pose_b not in POSES:
        return []

    frames_a = POSES[pose_a]
    frames_b = POSES[pose_b]

    if isinstance(frames_a[0], str):
        frames_a = [frames_a]
    if isinstance(frames_b[0], str):
        frames_b = [frames_b]

    frame_a = frames_a[-1]
    frame_b = frames_b[0]

    result = []
    max_lines = max(len(frame_a), len(frame_b))
    max_cols = max(
        (len(line) for line in frame_a), default=0
    )
    max_cols = max(
        max_cols, max((len(line) for line in frame_b), default=0)
    )

    padded_a = [line.ljust(max_cols) for line in frame_a]
    padded_b = [line.ljust(max_cols) for line in frame_b]

    for step in range(1, steps + 1):
        t = step / (steps + 1)
        interpolated = []
        for i in range(max_lines):
            if i >= len(padded_a):
                interpolated.append(padded_b[i] if i < len(padded_b) else " " * max_cols)
            elif i >= len(padded_b):
                interpolated.append(padded_a[i])
            else:
                line_a = padded_a[i]
                line_b = padded_b[i]
                blended = ""
                for j in range(max_cols):
                    ch_a = line_a[j] if j < len(line_a) else " "
                    ch_b = line_b[j] if j < len(line_b) else " "
                    blended += ch_b if t > 0.5 else ch_a
                interpolated.append(blended)
            result.append(interpolated)

    return result
