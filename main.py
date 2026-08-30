import random
import shutil
import sys
import time
from enum import IntEnum, StrEnum
from dataclasses import dataclass


# Screensaver options
PARTICLES = 200
PAUSE = 0.25

# ANSI Escape Codes
ANSI_HIDE_CURSOR = "\033[?25l"
ANSI_SHOW_CURSOR = "\033[?25h"
ANSI_TOP_LEFT = "\033[H"
ANSI_RESET = "\033[0m"
ANSI_ALT_BUFFER = "\033[?1049h"
ANSI_DEFAULT_BUFFER = "\033[?1049l"


class AnsiColor(StrEnum):
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"


class Shape(StrEnum):
    CROSS = "X"
    CIRCLE = "O"
    AT = "@"
    THORN = "þ"


class Speed(IntEnum):
    LOW = 1
    MEDIUM = 3
    HIGH = 5


@dataclass(slots=True)
class Particle:
    x: int
    y: int
    color: AnsiColor
    shape: Shape
    speed: Speed

    def move(self) -> None:
        """Move x and y  by a random amount based on speed."""
        self.x += random.randint(-self.speed, self.speed)
        self.y += random.randint(-self.speed, self.speed)
        

def generate_particle(ncol: int, nrow: int) -> Particle:
    return Particle(
        x=random.randint(0, ncol - 1),
        y=random.randint(0, nrow - 1),
        color=random.choice(list(AnsiColor)),
        shape=random.choice(list(Shape)),
        speed=random.choice(list(Speed)),
    )


def main():
    ncol, nrow = shutil.get_terminal_size()
    particles = [
        generate_particle(ncol, nrow) for _ in range(PARTICLES)
    ]
    try:
        # Enter alt buffer and hide cursor in one write
        sys.stdout.write(f"{ANSI_ALT_BUFFER}{ANSI_HIDE_CURSOR}")
        sys.stdout.flush()

        while True:
            # Re-fetch terminal dimensions dynamically
            # to prevent crash on window resize
            ncol, nrow = shutil.get_terminal_size()

            # Generate clean screen matrix
            screen = [[" " for _ in range(ncol)] for _ in range(nrow)]

            # Populate matrix with particles
            for particle in particles:
                px = particle.x % ncol
                py = particle.y % nrow
                # Reset color state immediately after CHAR
                # to avoid color leaking
                screen[py][px] = f"{particle.color}{particle.shape}{ANSI_RESET}"

            # Render entire frame in a single atomic I/O write
            frame = "\n".join("".join(row) for row in screen)
            sys.stdout.write(f"{ANSI_TOP_LEFT}{frame}")
            sys.stdout.flush()

            # Update particle positions
            for particle in particles:
                particle.move()

            time.sleep(PAUSE)

    except KeyboardInterrupt:
        sys.exit(0)
    finally:
        # Restore terminal defaults on exit
        sys.stdout.write(
            f"{ANSI_SHOW_CURSOR}{ANSI_DEFAULT_BUFFER}{ANSI_RESET}"
        )
        sys.stdout.flush()


if __name__ == "__main__":
    main()
