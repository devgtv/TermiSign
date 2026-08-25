import math
import time
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from animation.model3d import HumanoidModel, POSE_3D_MAP


class Renderer3D:
    def __init__(self, width=800, height=600, title="termiSign - LIBRAS 3D"):
        pygame.init()
        pygame.display.set_caption(title)
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 2)
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 1)
        pygame.display.gl_set_attribute(pygame.GL_DEPTH_SIZE, 24)
        pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLEBUFFERS, 1)
        pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLESAMPLES, 4)

        self.screen = pygame.display.set_mode(
            (width, height), DOUBLEBUF | OPENGL | RESIZABLE
        )
        self.width = width
        self.height = height
        self.model = HumanoidModel()

        self._setup_gl()
        self._setup_lighting()

        self.camera_x = 0
        self.camera_y = 2.2
        self.camera_z = 7.0

        self._current_char = ""
        self._current_desc = ""
        self._target_pose = "idle"
        self._transition_progress = 1.0
        self._prev_pose_params = {}
        self._target_pose_params = {}
        self._transition_speed = 3.0

    def _setup_gl(self):
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_LIGHT1)
        glEnable(GL_COLOR_MATERIAL)
        glEnable(GL_NORMALIZE)
        glEnable(GL_MULTISAMPLE)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glShadeModel(GL_SMOOTH)
        glClearColor(0.08, 0.08, 0.12, 1.0)
        glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)
        self._resize(self.width, self.height)

    def _setup_lighting(self):
        light0_pos = [2.0, 6.0, 4.0, 1.0]
        light0_diffuse = [0.9, 0.85, 0.8, 1.0]
        light0_specular = [1.0, 1.0, 1.0, 1.0]
        glLightfv(GL_LIGHT0, GL_POSITION, light0_pos)
        glLightfv(GL_LIGHT0, GL_DIFFUSE, light0_diffuse)
        glLightfv(GL_LIGHT0, GL_SPECULAR, light0_specular)

        light1_pos = [-3.0, 2.0, -2.0, 1.0]
        light1_diffuse = [0.25, 0.3, 0.45, 1.0]
        glLightfv(GL_LIGHT1, GL_POSITION, light1_pos)
        glLightfv(GL_LIGHT1, GL_DIFFUSE, light1_diffuse)

        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, [0.3, 0.3, 0.3, 1.0])
        glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 50.0)

    def _resize(self, width, height):
        if height == 0:
            height = 1
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, width / height, 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)

    def _update_camera(self):
        glLoadIdentity()
        gluLookAt(
            self.camera_x, self.camera_y, self.camera_z,
            0, 2.0, 0,
            0, 1, 0,
        )

    def set_pose(self, pose_name: str, animate=True):
        if pose_name == self._target_pose:
            return
        if animate and self._transition_progress < 1.0:
            self.model.set_pose(self._target_pose)
        self._prev_pose_params = {
            k: getattr(self.model, k) for k in POSE_3D_MAP.get("idle", {})
        }
        self._target_pose_params = POSE_3D_MAP.get(pose_name, POSE_3D_MAP["idle"])
        self._target_pose = pose_name
        self._transition_progress = 0.0

    def _interpolate_pose(self, dt):
        if self._transition_progress >= 1.0:
            return
        self._transition_progress += dt * self._transition_speed
        if self._transition_progress >= 1.0:
            self._transition_progress = 1.0
        t = self._transition_progress
        t = t * t * (3 - 2 * t)
        for key, target_val in self._target_pose_params.items():
            prev_val = self._prev_pose_params.get(key, 0)
            current = prev_val + (target_val - prev_val) * t
            setattr(self.model, key, current)

    def set_info(self, char: str = "", desc: str = ""):
        self._current_char = char.upper() if char else ""
        self._current_desc = desc

    def render_frame(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                return False
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE or event.key == K_q:
                    return False
            elif event.type == VIDEORESIZE:
                self.width, self.height = event.size
                self.screen = pygame.display.set_mode(
                    (self.width, self.height), DOUBLEBUF | OPENGL | RESIZABLE
                )
                self._resize(self.width, self.height)

        dt = 1.0 / 60.0
        self._interpolate_pose(dt)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        self._update_camera()

        glLightfv(GL_LIGHT0, GL_POSITION, [2.0, 6.0, 4.0, 1.0])
        glLightfv(GL_LIGHT1, GL_POSITION, [-3.0, 2.0, -2.0, 1.0])

        self._draw_grid()
        self.model.draw()
        self._draw_overlay_2d()

        pygame.display.flip()
        return True

    def _draw_grid(self):
        glDisable(GL_LIGHTING)
        glColor4f(0.2, 0.2, 0.25, 0.5)
        glBegin(GL_LINES)
        for i in range(-5, 6):
            glVertex3f(i, 0, -5)
            glVertex3f(i, 0, 5)
            glVertex3f(-5, 0, i)
            glVertex3f(5, 0, i)
        glEnd()
        glEnable(GL_LIGHTING)

    def _draw_overlay_2d(self):
        glDisable(GL_LIGHTING)
        glDisable(GL_DEPTH_TEST)
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, self.width, 0, self.height, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()

        self._draw_text_surface(
            f"Letra: {self._current_char}" if self._current_char else "termiSign",
            20, self.height - 40,
            color=(0.2, 1.0, 0.5),
            size=28,
        )
        if self._current_desc:
            self._draw_text_surface(
                self._current_desc, 20, self.height - 70,
                color=(0.8, 0.8, 0.8),
                size=18,
            )

        controls = "[ESC/Q] Sair"
        self._draw_text_surface(
            controls, 20, 15,
            color=(0.5, 0.5, 0.6),
            size=14,
        )

        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)

    def _draw_text_surface(self, text, x, y, color=(1, 1, 1), size=20):
        font = pygame.font.SysFont("monospace", size, bold=True)
        text_surface = font.render(text, True, (int(color[0]*255), int(color[1]*255), int(color[2]*255)))
        text_data = pygame.image.tostring(text_surface, "RGBA", True)
        tw, th = text_surface.get_size()
        glWindowPos2d(x, y)
        glDrawPixels(tw, th, GL_RGBA, GL_UNSIGNED_BYTE, text_data)

    def animate_sequence(self, signs: list[dict]) -> bool:
        for sign in signs:
            pose = sign.get("pose", "idle")
            char = sign.get("char", "")
            desc = sign.get("desc", "")
            duration = sign.get("duration", 0.8)

            self.set_pose(pose, animate=True)
            self.set_info(char, desc)

            start = time.time()
            while time.time() - start < duration:
                if not self.render_frame():
                    return False

            time.sleep(0.15)

        self.set_pose("idle", animate=True)
        self.set_info()
        settle_start = time.time()
        while time.time() - settle_start < 0.5:
            if not self.render_frame():
                return False

        return True

    def run_idle(self):
        return self.render_frame()

    def cleanup(self):
        pygame.quit()
