import curses
import time
from animation.poses import POSES, ACTIVE_POSE_MAP

COLOR_SKIN = 1
COLOR_BODY = 2
COLOR_FACE = 3
COLOR_HAND = 4
COLOR_TEXT = 5
COLOR_BG = 6
COLOR_LETTER = 7


def _setup_colors():
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(COLOR_SKIN, curses.COLOR_YELLOW, -1)
    curses.init_pair(COLOR_BODY, curses.COLOR_CYAN, -1)
    curses.init_pair(COLOR_FACE, curses.COLOR_WHITE, -1)
    curses.init_pair(COLOR_HAND, curses.COLOR_YELLOW, -1)
    curses.init_pair(COLOR_TEXT, curses.COLOR_GREEN, -1)
    curses.init_pair(COLOR_BG, curses.COLOR_BLACK, -1)
    curses.init_pair(COLOR_LETTER, curses.COLOR_MAGENTA, -1)


def _colorize_line(line: str, line_idx: int) -> list[tuple[str, int]]:
    result = []
    for ch in line:
        if line_idx <= 5:
            pair = COLOR_FACE
        elif line_idx <= 11:
            pair = COLOR_BODY
        elif "(" in ch or "\\" in ch or "/" in ch:
            pair = COLOR_HAND
        else:
            pair = COLOR_SKIN
        result.append((ch, pair))
    return result


class Renderer:
    def __init__(self, stdscr):
        self._stdscr = stdscr
        curses.curs_set(0)
        curses.nonl()
        stdscr.nodelay(True)
        stdscr.timeout(50)
        _setup_colors()
        self._current_char = ""
        self._current_desc = ""
        self._footer_text = ""
        self._is_active_anim = False

    def render_pose(
        self,
        pose_name: str,
        char: str = "",
        desc: str = "",
        is_active: bool = False,
    ):
        self._current_char = char.upper() if char else ""
        self._current_desc = desc
        self._is_active_anim = is_active

        if pose_name not in POSES:
            pose_name = "idle"

        frames = POSES[pose_name]
        if isinstance(frames[0], str):
            frames = [frames]

        for frame in frames:
            self._draw_frame(frame)
            if is_active:
                time.sleep(0.15)
            else:
                break

    def _draw_frame(self, frame: list[str]):
        self._stdscr.erase()
        height, width = self._stdscr.getmaxyx()

        start_y = 1
        start_x = max(0, (width - len(frame[0])) // 2)

        for i, line in enumerate(frame):
            y = start_y + i
            if y >= height - 4:
                break
            colored = _colorize_line(line, i)
            x = start_x
            for ch, pair in colored:
                if x < width - 1:
                    try:
                        self._stdscr.addch(y, x, ch, curses.color_pair(pair))
                    except curses.error:
                        pass
                    x += 1

        info_y = start_y + len(frame) + 1
        if info_y < height - 3 and self._current_char:
            label = f"  Letra: {self._current_char}  "
            x_pos = max(0, (width - len(label)) // 2)
            try:
                self._stdscr.addstr(
                    info_y, x_pos, label, curses.color_pair(COLOR_LETTER) | curses.A_BOLD
                )
            except curses.error:
                pass

        if info_y + 1 < height - 2 and self._current_desc:
            desc_text = f"  {self._current_desc}  "
            x_pos = max(0, (width - len(desc_text)) // 2)
            try:
                self._stdscr.addstr(
                    info_y + 1, x_pos, desc_text, curses.color_pair(COLOR_TEXT)
                )
            except curses.error:
                pass

        footer = " [Q] Sair  |  termiSign - Traducao de Audio para LIBRAS "
        if height > 2:
            try:
                self._stdscr.addstr(
                    height - 1, 0, footer[: width - 1], curses.color_pair(COLOR_TEXT)
                )
            except curses.error:
                pass

        self._stdscr.refresh()

    def render_idle(self):
        self._draw_frame(POSES["idle"])

    def render_text(self, text: str):
        self._footer_text = text

    def render_message(self, msg: str, y_offset: int = 0):
        height, width = self._stdscr.getmaxyx()
        y = max(0, (height // 2) + y_offset)
        x = max(0, (width - len(msg)) // 2)
        try:
            self._stdscr.addstr(y, x, msg, curses.color_pair(COLOR_TEXT) | curses.A_BOLD)
        except curses.error:
            pass

    def animate_sequence(self, signs: list[dict]) -> bool:
        for sign in signs:
            pose = sign.get("pose", "idle")
            char = sign.get("char", "")
            desc = sign.get("desc", "")
            is_active = sign.get("movement", False)
            duration = sign.get("duration", 0.8)

            if is_active and pose in ACTIVE_POSE_MAP:
                frame_sequence = ACTIVE_POSE_MAP[pose]
                start_time = time.time()
                while time.time() - start_time < duration:
                    for frame_pose in frame_sequence:
                        frames = POSES.get(frame_pose, POSES["idle"])
                        if isinstance(frames[0], str):
                            frames = [frames]
                        for frame in frames:
                            self._draw_frame(frame)
                            if self._stdscr.getch() == ord("q"):
                                return False
                            time.sleep(0.12)
            else:
                frames = POSES.get(pose, POSES["idle"])
                if isinstance(frames[0], str):
                    frames = [frames]
                start_time = time.time()
                while time.time() - start_time < duration:
                    for frame in frames:
                        self._draw_frame(frame)
                        if self._stdscr.getch() == ord("q"):
                            return False
                        time.sleep(0.05)

            time.sleep(0.2)

        self.render_idle()
        return True
