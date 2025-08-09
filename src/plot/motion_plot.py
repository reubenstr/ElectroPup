from enum import Enum
from time import time, sleep
import numpy as np
import matplotlib.pyplot as plt
from typing import List, Dict
from system.quadruped.quad import LegName


class Phase(Enum):
    STANCE = 0
    SWING = 1


class GaitPattern:
    def __init__(self, name: str, period: float, duty_factor: float, phase_offsets: Dict[LegName, float]):
        self.name = name

        # Duration of one complete gait cycle\
        # Units in seconds
        self.period = period

        # Percent of time in stand (power stroke).
        # Range: [0, 1].
        # Example: 0.75 = 75% stance, 25% swing
        self.duty_factor = duty_factor

        # Dict[LegName, float] determines when during the gait cycle that leg begins the swing phase.
        # Range: [0, 1],
        self.phase_offsets = phase_offsets

    def get_leg_phase_time(self, leg: LegName, time: float) -> tuple[Phase, float]:
        cycle_time = time % self.period
        phase_time = (cycle_time / self.period - self.phase_offsets[leg]) % 1.0
        phase = Phase.STANCE if phase_time < self.duty_factor else Phase.SWING

        # Normalize phase time, example:
        # STANCE: [0, duty_factor]
        # SWING : [duty_factor, 1.0]
        normalized_time = phase_time / self.duty_factor if phase == Phase.STANCE else (phase_time - self.duty_factor) / (1 - self.duty_factor)

        return phase, normalized_time


def bezier_curve(t, points):
    """Evaluate a Bezier curve at t ∈ [0, 1] using De Casteljau's algorithm."""
    p = np.array(points)
    while len(p) > 1:
        p = (1 - t) * p[:-1] + t * p[1:]
    return p[0]


def foot_trajectory_bezier(phase: Phase, phase_time: float, stride_length=0.2, step_height=0.05):
    """Return foot (x, z) using Bezier swing and linear stance."""
    if phase == Phase.STANCE:
        # Linear backward motion (stroke)
        x = (1 - phase_time) * stride_length - stride_length / 2
        z = 0
    elif phase == Phase.SWING:
        # Bezier swing (retract/touchdown)
        control_points = np.array(
            [
                [-stride_length / 2, 0],
                [-stride_length, 0],
                [-stride_length, step_height],
                [0, step_height],
                [stride_length, step_height],
                [stride_length, 0],
                [stride_length / 2, 0],
            ]
        )
        # [p0, p1, p2, p3]

        x, z = bezier_curve(phase_time, control_points)
    return x, z


def foot_trajectory_sin(phase: Phase, phase_time: float, stride_length=0.2, step_height=0.05):
    """Return foot (x, z) position based on phase and normalized phase time (0-1)."""
    if phase == Phase.STANCE:
        # Stance: foot moves backward linearly along x, stays on ground
        x = (1 - phase_time) * stride_length - stride_length / 2
        z = 0
    else:
        # Swing: foot moves forward with parabolic height
        x = phase_time * stride_length - stride_length / 2
        z = step_height * np.sin(np.pi * phase_time)
    return x, z


walk_gait = GaitPattern(
    name="Walk",
    period=1.0,
    duty_factor=0.75,
    phase_offsets={
        LegName.LF: 0.0,
        LegName.RR: 0.25,
        LegName.RF: 0.5,
        LegName.LR: 0.75,
    },
)

trot_gait = GaitPattern(
    name="Trot",
    period=0.6,
    duty_factor=0.5,
    phase_offsets={
        LegName.LF: 0.0,
        LegName.RR: 0.0,
        LegName.RF: 0.5,
        LegName.LR: 0.5,
    },
)


def simulate(gait: GaitPattern, duration: float, timestep: float = 0.1):
    t = 0.0
    while t < duration:
        print(f"\nTime: {t:.2f}s - Gait: {gait.name}")
        for leg in LegName:
            phase, _ = gait.get_leg_phase_time(leg, t)
            symbol = "█" if phase == Phase.STANCE else " "
            print(f"{leg.value:12}: {symbol} ({phase.name})")
        sleep(timestep)
        t += timestep


def plot_foot_trajectories(gait: GaitPattern, duration=1.5, timestep=0.02):
    times = np.arange(0, duration, timestep)
    leg_positions = {leg: {"x": [], "z": []} for leg in LegName}

    for t in times:
        for leg in LegName:
            phase, phase_time = gait.get_leg_phase_time(leg, t)
            x, z = foot_trajectory_bezier(phase, phase_time)
            leg_positions[leg]["x"].append(x)
            leg_positions[leg]["z"].append(z)

    # Plot
    fig, ax = plt.subplots(figsize=(8, 4))
    for leg in LegName:
        ax.plot(leg_positions[leg]["x"], leg_positions[leg]["z"], label=leg.value, marker="o", markersize=3, linestyle="-", linewidth=1.0)

    ax.set_xlabel("X (forward) meters")
    ax.set_ylabel("Z (height) meters")
    ax.set_title(f"Foot Trajectories - {gait.name}")
    ax.legend()
    ax.grid(True)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":

    plot_foot_trajectories(walk_gait, duration=1, timestep=0.01)

    # print("Simulating Walk...")
    # simulate(walk_gait, duration=30.0)

    # print("\nSimulating Trot...")
    # simulate(trot_gait, duration=3.0)
