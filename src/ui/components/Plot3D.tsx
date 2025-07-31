import React, { useEffect, useState, useMemo, useRef } from 'react';
import { Platform, View, Text, StyleSheet, LayoutChangeEvent, TouchableOpacity } from 'react-native';
import { QuadData } from '@/interfaces/messages';
import { Switch } from 'react-native-paper';
import { PlotData } from '@/interfaces/messages';

interface Plot3DProps {
  quadData?: QuadData;
}

export default function Plot3D({ quadData }: Plot3DProps) {
  const [Plot, setPlot] = useState<any>(null);
  const [hold, setHold] = useState(false);
  const [plotWidth, setPlotWidth] = useState(0);
  const [plotHeight, setPlotHeight] = useState(0);
  const [checkedValues, setCheckedValues] = useState({ grid: false, x: true, y: true, z: true, sim: true, live: true });

  const lastUpdateRef = useRef<number>(0);
  const [throttledPlotData, setThrottledPlotData] = useState<any[]>([]);

  const max_plot_refresh_rate_ms: number = 50

  const gridBoundry = 400;
  const legColor = '#00cd00';

  useEffect(() => {
    if (Platform.OS === 'web') {
      if (typeof self === 'undefined') {
        (global as any).self = global;
      }
      import('react-plotly.js').then((mod) => {
        setPlot(() => mod.default);
      }).catch(err => {
        console.error("Failed to load react-plotly.js", err);
      });
    }
  }, []);

  const onLayoutContainer = (event: LayoutChangeEvent) => {
    const { width, height } = event.nativeEvent.layout;
    setPlotWidth(width);
    setPlotHeight(height);
  };

  const computePlotData = useMemo(() => {
    return (quadData: QuadData) => {
      const plotData: any[] = []

      if (quadData.plotSim && checkedValues.sim) {
        plotData.push(...generatePlotData(quadData.plotSim));
      }

      if (quadData.plotLive && checkedValues.live) {
        plotData.push(...generatePlotData(quadData.plotLive));
      }

      return plotData;
    };
  }, [legColor, checkedValues]);

  useEffect(() => {
    if (quadData) {
      if (hold) return;
      if (Date.now() - lastUpdateRef.current > max_plot_refresh_rate_ms) {
        lastUpdateRef.current = Date.now();
        setThrottledPlotData(computePlotData(quadData));
      }
    }
  }, [quadData, hold, computePlotData]);

  const defaultZoomLevel = 0.7;

  const getGridSettings = (showGrid: boolean) => {
    if (showGrid) {
      return {
        xaxis: {
          range: [-gridBoundry, gridBoundry],
          title: 'X',
          showline: true,
          showgrid: true,
          zeroline: true,
          showticklabels: true
        },
        yaxis: {
          range: [-gridBoundry, gridBoundry],
          title: 'Y',
          showline: true,
          showgrid: true,
          zeroline: true,
          showticklabels: true
        },
        zaxis: {
          range: [-gridBoundry, gridBoundry],
          title: 'Z',
          showline: true,
          showgrid: true,
          zeroline: true,
          showticklabels: true
        }
      }
    } else {
      return {
        xaxis: { range: [-gridBoundry, gridBoundry], showticklabels: false, showgrid: false, zeroline: false, showspikes: false, title: '' },
        yaxis: { range: [-gridBoundry, gridBoundry], showticklabels: false, showgrid: false, zeroline: false, showspikes: false, title: '' },
        zaxis: { range: [-gridBoundry, gridBoundry], showticklabels: false, showgrid: false, zeroline: false, showspikes: false, title: '' }
      }
    }
  }

  const layout = useMemo(() => ({
    scene: {
      ...getGridSettings(checkedValues.grid),
      camera: {
        eye: { x: checkedValues.x ? defaultZoomLevel : 0, y: checkedValues.y ? defaultZoomLevel : 0, z: checkedValues.z ? defaultZoomLevel : 0 },
        center: {
          x: 0,
          y: 0,
          z: 0
        },
      },
      aspectmode: 'cube',
    },
    margin: { t: 10, b: 10, l: 10, r: 10 },
    paper_bgcolor: 'rgba(0, 0, 0, 0)',
    plot_bgcolor: 'rgba(0, 0, 0, 0)',
    font: { color: 'white' },
  }), [checkedValues, gridBoundry]);

  const config = useMemo(() => ({
    displayModeBar: false,
    responsive: true,
  }), []);

  const plotComponentStyle = useMemo(() => ({
    width: plotWidth,
    height: plotHeight,
  }), [plotWidth, plotHeight]);

  const toggleCheckbox = (key: string) => {
    setCheckedValues((prev) => ({
      ...prev,
      [key]: !prev[key],
    }));
  };

  const handleHoldClick = () => {
    console.log(hold)
    setHold(!hold);
  };


  const generatePlotData = (plotData: PlotData): any[] => {
    const newPlotData: any = [];

    if (plotData.body) {
      newPlotData.push({
        x: plotData.body.x,
        y: plotData.body.y,
        z: plotData.body.z,
        type: 'scatter3d',
        mode: 'markers+lines',
        name: 'body',
        showlegend: false,
        marker: { color: 'blue' },
        line: {
          shape: 'linear',
          width: 5, color: 'black'
        }
      });
    }

    if (plotData.legs) {
      plotData.legs.map((leg, index) => {
        newPlotData.push({
          x: leg.x,
          y: leg.y,
          z: leg.z,
          type: 'scatter3d',
          mode: 'markers+lines',
          name: leg.name,
          showlegend: false,
          line: { shape: 'linear', width: 5, color: 'black' },
          marker: { color: legColor }
        });
      });
    }

    if (plotData.mesh) {
      newPlotData.push(
        {
          x: plotData.mesh.x,
          y: plotData.mesh.y,
          z: plotData.mesh.z,
          type: 'mesh3d',
          name: 'mesh',
          showlegend: false,
          opacity: 0.1,
          color: '#ffa801'
        });
    }

    if (plotData.trajectories) {
      plotData.trajectories.map((trajectory, index) => {
        const pI = trajectory.x.map((_, i) => i);
        const m = { size: 4, color: pI, colorscale: [[0, '#4a8cffff'], [1, '#0000ffff']] };
        newPlotData.push({
          x: trajectory.x,
          y: trajectory.y,
          z: trajectory.z,
          type: 'scatter3d',
          mode: 'markers+lines',
          name: trajectory.name,
          showlegend: false,
          line: { shape: 'linear', width: 6, color: 'black' },
          marker: m
        });
      });
    }

    if (plotData.transitions) {
      plotData.transitions.map((trajectory, index) => {
        newPlotData.push({
          x: trajectory.x,
          y: trajectory.y,
          z: trajectory.z,
          type: 'scatter3d',
          mode: 'markers+lines',
          name: `soft-${index}`,
          showlegend: false,
          line: { shape: 'linear', width: 6, color: 'black' },
          marker: { size: 4, color: 'orange' }
        });
      });
    }

    if (plotData.rings) {
      plotData.rings.forEach((ring, index) => {
        newPlotData.push({
          x: ring.x,
          y: ring.y,
          z: ring.z,
          type: 'scatter3d',
          mode: 'markers+lines',
          name: `ring-${index}`,
          showlegend: false,
          line: { shape: 'linear', width: 6, color: 'black' },
          marker: { size: 4, color: '#dddd00' }
        });
      });
    }

    if (plotData.holdTrajectories) {
      plotData.holdTrajectories.map((trajectory, index) => {
        const pI = trajectory.x.map((_, i) => i);
        const m = { size: 4, color: pI, colorscale: [[0, '#ff0000ff'], [1, '#9e0000ff']] };
        newPlotData.push({
          x: trajectory.x,
          y: trajectory.y,
          z: trajectory.z,
          type: 'scatter3d',
          mode: 'markers+lines',
          name: trajectory.name,
          showlegend: false,
          line: { shape: 'linear', width: 6, color: 'black' },
          marker: m
        });
      });
    }

    return newPlotData;
  }

  if (Platform.OS !== 'web') {
    return (
      <Text style={styles.errorText}>Plot not supported on native platform.</Text>
    );
  }

  if (!Plot) {
    return (
      <View style={styles.container} onLayout={onLayoutContainer}>
        <Text style={styles.loadingText}>Loading plot library...</Text>
      </View>
    );
  }

  if (plotWidth === 0 || plotHeight === 0) {
    return (
      <View style={styles.container} onLayout={onLayoutContainer}>
        <Text style={styles.loadingText}>Measuring layout...</Text>
      </View>
    );
  }

  if (!quadData) {
    return (
      <View style={styles.container} onLayout={onLayoutContainer}>
        <Text style={styles.loadingText}>Waiting for data...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container} onLayout={onLayoutContainer}>
      <View style={styles.checkboxesRow}>
        <View style={styles.checkboxContainer}>
          <Switch
            value={checkedValues.grid}
            onValueChange={() => toggleCheckbox('grid')}
            color={'#0077ff'}
          />
          <Text style={styles.checkboxText}>Grid</Text>
          <Switch
            value={checkedValues.x}
            onValueChange={() => toggleCheckbox('x')}
            color={'#0077ff'}
          />
          <Text style={styles.checkboxText}>X</Text>
          <Switch
            value={checkedValues.y}
            onValueChange={() => toggleCheckbox('y')}
            color={'#0077ff'}
          />
          <Text style={styles.checkboxText}>Y</Text>
          <Switch
            value={checkedValues.z}
            onValueChange={() => toggleCheckbox('z')}
            color={'#0077ff'}
          />
          <Text style={styles.checkboxText}>Z</Text>
        </View>
        <TouchableOpacity
          style={styles.holdButton}
          onPress={() => handleHoldClick()}>
          <Text style={styles.holdButtonText}>{hold ? 'UNHOLD' : 'HOLD'}</Text>
        </TouchableOpacity>
        <Switch
          value={checkedValues.sim}
          onValueChange={() => toggleCheckbox('sim')}
          color={'#0077ff'}
        />
        <Text style={styles.checkboxText}>SIM</Text>
        <Switch
          value={checkedValues.live}
          onValueChange={() => toggleCheckbox('live')}
          color={'#0077ff'}
        />
        <Text style={styles.checkboxText}>LIVE</Text>
      </View>
      <Plot
        data={throttledPlotData}
        layout={layout}
        style={plotComponentStyle}
        config={config}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    width: '100%',
    alignItems: 'center',
    justifyContent: 'center',

  },
  checkboxesRow: {
    position: 'absolute',
    zIndex: 9999,
    top: 5,
    flexDirection: 'row',
    justifyContent: 'space-around',
    alignItems: 'center',
  },
  checkboxContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginHorizontal: 20,
  },
  checkboxText: {
    paddingLeft: 5,
    paddingRight: 15,
    color: 'white'
  },
  holdButton: {
    paddingVertical: 5,
    paddingHorizontal: 5,
    borderRadius: 4,
    backgroundColor: '#0077ff',
    width: 75,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 30
  },
  holdButtonText: {

  },
  loadingText: {
    fontSize: 18,
    color: 'white',
  },
  errorText: {
    fontSize: 18,
    color: 'red',
  },

});

