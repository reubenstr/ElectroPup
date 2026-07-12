/* Motor id -> human-readable joint name. Keys match the motor keys the robot
   publishes in `data.motors`. Order here drives display order. */
export const motorNames = {
  // Left side.
  FLA: "front left abduction",
  FLH: "front left hip",
  FLK: "front left knee",
  BLA: "back left abduction",
  BLH: "back left hip",
  BLK: "back left knee",
  // Right side.
  FRA: "front right abduction",
  FRH: "front right hip",
  FRK: "front right knee",
  BRA: "back right abduction",
  BRH: "back right hip",
  BRK: "back right knee",
} as const;

export type MotorKey = keyof typeof motorNames;
