import { useEffect, useState, useMemo, useRef } from "react";
import {
  Platform,
  View,
  Text,
  LayoutChangeEvent,
} from "react-native";
import { StyleSheet, useUnistyles } from "react-native-unistyles";
import { createText } from "@/styles/themeComponents";
import type { AppTheme } from "@/styles/themes";
import Button from "@/components/primatives/Button";
import { Data, PlotData, PlotDataExtras } from "@/services/data/dataTypes";

const MAX_REFRESH_MS = 50;
const GRID_BOUNDARY = 400;
const DEFAULT_ZOOM = 0.7;

type Toggles = {
  grid: boolean;
  x: boolean;
  y: boolean;
  z: boolean;
  sim: boolean;
  live: boolean;
};

type Skeleton = AppTheme["colors"]["robot"]["sim"];

interface Plot3DProps {
  data?: Data;
}

export default function Plot3D({ data }: Plot3DProps) {
  const { theme } = useUnistyles();
  const robot = theme.colors.robot;

  const [Plot, setPlot] = useState<React.ComponentType<any> | null>(null);
  const [hold, setHold] = useState(false);
  const [size, setSize] = useState({ width: 0, height: 0 });
  const [toggles, setToggles] = useState<Toggles>({
    grid: false,
    x: true,
    y: true,
    z: true,
    sim: true,
    live: true,
  });

  const lastUpdateRef = useRef(0);
  const [traces, setTraces] = useState<any[]>([]);

  /* plotly.js touches `self`, so it can only load in the browser. Pull in the
     slim gl3d bundle through react-plotly's factory to keep Metro from walking
     the full plotly source tree (which OOMs the Pi build). */
  useEffect(() => {
    if (Platform.OS !== "web") return;
    if (typeof self === "undefined") {
      (globalThis as any).self = globalThis;
    }
    let cancelled = false;
    Promise.all([
      import("react-plotly.js/factory"),
      import("plotly.js-gl3d-dist-min"),
    ])
      .then(([factory, plotly]) => {
        if (cancelled) return;
        const create = (factory as any).default;
        const Plotly = (plotly as any).default ?? plotly;
        setPlot(() => create(Plotly));
      })
      .catch((err) => console.error("[plot] failed to load plotly", err));
    return () => {
      cancelled = true;
    };
  }, []);

  const buildTraces = useMemo(() => {
    return (source: Data) => {
      const out: any[] = [];
      if (source.plotSim && toggles.sim) {
        out.push(...skeletonTraces(source.plotSim, robot.sim, robot.line));
      }
      if (source.plotLive && toggles.live) {
        out.push(...skeletonTraces(source.plotLive, robot.live, robot.line));
      }
      if (source.plotExtras) {
        out.push(...extrasTraces(source.plotExtras, robot));
      }
      return out;
    };
  }, [toggles.sim, toggles.live, robot]);

  useEffect(() => {
    if (!data || hold) return;
    const now = Date.now();
    if (now - lastUpdateRef.current < MAX_REFRESH_MS) return;
    lastUpdateRef.current = now;
    setTraces(buildTraces(data));
  }, [data, hold, buildTraces]);

  const layout = useMemo(
    () => ({
      scene: {
        ...axisSettings(toggles.grid),
        camera: {
          eye: {
            x: toggles.x ? DEFAULT_ZOOM : 0,
            y: toggles.y ? DEFAULT_ZOOM : 0,
            z: toggles.z ? DEFAULT_ZOOM : 0,
          },
          center: { x: 0, y: 0, z: 0 },
        },
        aspectmode: "cube",
      },
      margin: { t: 10, b: 10, l: 10, r: 10 },
      paper_bgcolor: "rgba(0,0,0,0)",
      plot_bgcolor: "rgba(0,0,0,0)",
      font: { color: theme.colors.text.primary },
    }),
    [toggles.grid, toggles.x, toggles.y, toggles.z, theme.colors.text.primary],
  );

  const config = useMemo(
    () => ({ displayModeBar: false, responsive: true }),
    [],
  );

  const onLayout = (e: LayoutChangeEvent) => {
    const { width, height } = e.nativeEvent.layout;
    setSize({ width, height });
  };

  const toggle = (key: keyof Toggles) =>
    setToggles((prev) => ({ ...prev, [key]: !prev[key] }));

  if (Platform.OS !== "web") {
    return (
      <View style={styles.container}>
        <Text style={styles.error}>Plot not supported on native platform.</Text>
      </View>
    );
  }

  let overlay: string | null = null;
  if (!Plot) overlay = "Loading plot library...";
  else if (size.width === 0 || size.height === 0) overlay = "Measuring layout...";
  else if (!data) overlay = "Waiting for data...";

  return (
    <View style={styles.container} onLayout={onLayout}>
      <View style={styles.toolbar}>
        <Button label="Grid" buttonType="action" isSelected={toggles.grid} onPress={() => toggle("grid")} />
        <Button label="X" buttonType="action" isSelected={toggles.x} onPress={() => toggle("x")} />
        <Button label="Y" buttonType="action" isSelected={toggles.y} onPress={() => toggle("y")} />
        <Button label="Z" buttonType="action" isSelected={toggles.z} onPress={() => toggle("z")} />
        <Button label={hold ? "Unhold" : "Hold"} buttonType="warning" isSelected={hold} onPress={() => setHold((h) => !h)} />
        <Button label="Sim" buttonType="success" isSelected={toggles.sim} onPress={() => toggle("sim")} />
        <Button label="Live" buttonType="danger" isSelected={toggles.live} onPress={() => toggle("live")} />
      </View>

      {overlay ? (
        <Text style={styles.overlay}>{overlay}</Text>
      ) : (
        Plot && (
          <Plot
            data={traces}
            layout={layout}
            config={config}
            style={{ width: size.width, height: size.height }}
          />
        )
      )}
    </View>
  );
}

/* Body + legs as connected markers/lines, support polygon as a translucent
   mesh. Feet (the last point of each leg) get their own marker color. */
function skeletonTraces(
  plot: PlotData,
  colors: Skeleton,
  lineColor: string,
): any[] {
  const out: any[] = [];
  const line = { shape: "linear", width: 5, color: lineColor };

  if (plot.body) {
    out.push({
      x: plot.body.x,
      y: plot.body.y,
      z: plot.body.z,
      type: "scatter3d",
      mode: "markers+lines",
      name: "body",
      showlegend: false,
      line,
      marker: { color: colors.body },
    });
  }

  if (plot.legs) {
    for (const leg of plot.legs) {
      const markerColors = leg.x.map((_, i) =>
        i === leg.x.length - 1 ? colors.foot : colors.joint,
      );
      out.push({
        x: leg.x,
        y: leg.y,
        z: leg.z,
        type: "scatter3d",
        mode: "markers+lines",
        name: leg.name,
        showlegend: false,
        line,
        marker: { color: markerColors },
      });
    }
  }

  if (plot.support) {
    out.push({
      x: plot.support.x,
      y: plot.support.y,
      z: plot.support.z,
      type: "mesh3d",
      name: "support",
      showlegend: false,
      opacity: 0.15,
      color: colors.foot,
    });
  }

  return out;
}

function extrasTraces(
  extras: PlotDataExtras,
  robot: AppTheme["colors"]["robot"],
): any[] {
  const out: any[] = [];
  const line = { shape: "linear", width: 6, color: robot.line };

  const gradient = (
    points: number[],
    scale: [[number, string], [number, string]],
  ) => ({
    size: 4,
    color: points.map((_, i) => i),
    colorscale: scale,
  });

  extras.trajectories?.forEach((t) => {
    out.push({
      x: t.x, y: t.y, z: t.z,
      type: "scatter3d", mode: "markers+lines", name: t.name, showlegend: false,
      line,
      marker: gradient(t.x, [[0, robot.trajectory.start], [1, robot.trajectory.end]]),
    });
  });

  extras.transitions?.forEach((t, i) => {
    out.push({
      x: t.x, y: t.y, z: t.z,
      type: "scatter3d", mode: "markers+lines", name: `transition-${i}`, showlegend: false,
      line,
      marker: { size: 4, color: robot.transition },
    });
  });

  extras.rings?.forEach((ring, i) => {
    out.push({
      x: ring.x, y: ring.y, z: ring.z,
      type: "scatter3d", mode: "markers+lines", name: `ring-${i}`, showlegend: false,
      line,
      marker: { size: 4, color: robot.ring },
    });
  });

  extras.holdTrajectories?.forEach((t) => {
    out.push({
      x: t.x, y: t.y, z: t.z,
      type: "scatter3d", mode: "markers+lines", name: t.name, showlegend: false,
      line,
      marker: gradient(t.x, [[0, robot.hold.start], [1, robot.hold.end]]),
    });
  });

  return out;
}

function axisSettings(showGrid: boolean) {
  const range = [-GRID_BOUNDARY, GRID_BOUNDARY];
  if (showGrid) {
    const axis = (title: string) => ({
      range,
      title,
      showline: true,
      showgrid: true,
      zeroline: true,
      showticklabels: true,
    });
    return { xaxis: axis("X"), yaxis: axis("Y"), zaxis: axis("Z") };
  }
  const hidden = {
    range,
    title: "",
    showticklabels: false,
    showgrid: false,
    zeroline: false,
    showspikes: false,
  };
  return { xaxis: hidden, yaxis: hidden, zaxis: hidden };
}

const styles = StyleSheet.create((theme) => ({
  container: {
    flex: 1,
    width: "100%",
    alignItems: "center",
    justifyContent: "center",
  },
  toolbar: {
    position: "absolute",
    top: theme.padding.inset,
    zIndex: theme.zIndex.control,
    flexDirection: "row",
    gap: theme.gap.control,
    flexWrap: "wrap",
    justifyContent: "center",
  },
  overlay: {
    color: theme.colors.text.secondary,
    ...createText(theme, "body"),
  },
  error: {
    color: theme.colors.text.error,
    ...createText(theme, "body"),
  },
}));
