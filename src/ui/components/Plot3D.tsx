import React, { useRef, useEffect, useState, useMemo } from 'react';
import { View } from 'react-native';
import { GLView } from 'expo-gl';
import { Renderer } from 'expo-three';
import * as THREE from 'three';

import { QuadData } from '@/interfaces/messages';


const legColor = '#00cd00';


interface Plot3DProps {
  quadData?: QuadData;
}

export default function Plot3D({ quadData }: Plot3DProps) {

  const isDragging = useRef(false);
  const lastMousePosition = useRef({ x: 0, y: 0 });
  const rotation = useRef({ x: 0, y: 0 });
  const pan = useRef({ x: 0, y: 0 });
  const cameraRef = useRef();
  const groupRef = useRef();

  //////////////////////////////

  const [pointSets, setPointSets] = useState([]);


  const [hold, setHold] = useState(false);
  const lastUpdateRef = useRef<number>(0);
  const [throttledPlotData, setThrottledPlotData] = useState<any[]>([]);
  const [checkedValues, setCheckedValues] = useState({ x: true, y: true, z: true, sim: true, live: true });


  const max_plot_refresh_rate_ms: number = 50

  useEffect(() => {
    if (quadData) {
      if (hold) return;
      if (Date.now() - lastUpdateRef.current > max_plot_refresh_rate_ms) {
        lastUpdateRef.current = Date.now();
        setThrottledPlotData(computePlotData(quadData));
        console.log(throttledPlotData)
      }
    }
  }, [quadData]);


  const computePlotData = useMemo(() => {
    return (quadData: QuadData) => {
      const plotData: any[] = []

      if (quadData.plotSim && checkedValues.sim) {
        //plotData.push(...generatePlotData(quadData.plotSim));
        plotData.push(...generatePlotData(quadData.plotSim));
      }

      if (quadData.plotLive && checkedValues.live) {
        plotData.push(...generatePlotData(quadData.plotLive));
      }
    
      return plotData;
    };
  }, [legColor, checkedValues]);


  const generatePlotData = (plotData: any): any[] => {
    const newPointSets = [];

    if (plotData.body) {           
        const points = plotData.body.points.map((point) =>
          new THREE.Vector3(point.x, point.y, point.z)
        );
        points.push(points[0])
        newPointSets.push(points);   
    }

    if (plotData.legs) {
      plotData.legs.forEach((leg) => {
        const points = leg.points.map((point) =>
          new THREE.Vector3(point.x, point.y, point.z)
        );
        newPointSets.push(points);
      });
    }

    return newPointSets;
  }



  function createCircleTexture(size = 64) {
    const canvas = document.createElement('canvas');
    canvas.width = canvas.height = size;
    const ctx = canvas.getContext('2d');

    // Draw circle
    ctx.beginPath();
    ctx.arc(size / 2, size / 2, size / 2, 0, Math.PI * 2);
    ctx.fillStyle = 'white';
    ctx.fill();

    const texture = new THREE.CanvasTexture(canvas);
    texture.needsUpdate = true;
    return texture;
  }

  const onContextCreate = async (gl) => {
    const { drawingBufferWidth: width, drawingBufferHeight: height } = gl;

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(75, width / height, 0.1, 1000);
    camera.position.set(0, 0, 1);
    cameraRef.current = camera;

    const renderer = new Renderer({ gl });
    renderer.setSize(width, height);
    renderer.setClearColor(0x000000, 1);

    const group = new THREE.Group();
    groupRef.current = group;

    throttledPlotData.forEach((points, i) => {
      const pointMat = new THREE.PointsMaterial({
        color: 0x00ff00,
        size: 0.05,
        sizeAttenuation: true,
        map: createCircleTexture(),
        alphaTest: 0.5,
        transparent: true,
      });
      // Points
      const pointGeom = new THREE.BufferGeometry().setFromPoints(points);
      const pointCloud = new THREE.Points(pointGeom, pointMat);
      group.add(pointCloud);

      // Lines (connecting points within the same set)
      const lineMat = new THREE.LineBasicMaterial({ color: 0x00ff00 });
      const lineGeom = new THREE.BufferGeometry().setFromPoints(points);
      const line = new THREE.Line(lineGeom, lineMat);
      group.add(line);
    });

    scene.add(group);

    const light = new THREE.AmbientLight(0xffffff, 0.6);
    scene.add(light);

    const canvas = gl.canvas;

    // Mouse controls
    canvas.addEventListener('mousedown', (e) => {
      isDragging.current = true;
      lastMousePosition.current = { x: e.clientX, y: e.clientY };
    });

    canvas.addEventListener('mouseup', () => {
      isDragging.current = false;
    });

    canvas.addEventListener('mouseleave', () => {
      isDragging.current = false;
    });

    canvas.addEventListener('mousemove', (e) => {
      if (!isDragging.current) return;

      const dx = e.clientX - lastMousePosition.current.x;
      const dy = e.clientY - lastMousePosition.current.y;
      lastMousePosition.current = { x: e.clientX, y: e.clientY };

      if (e.shiftKey) {
        // PAN CAMERA
        const panSpeed = 0.01;
        pan.current.x -= dx * panSpeed;
        pan.current.y += dy * panSpeed;
        camera.position.x = pan.current.x;
        camera.position.y = pan.current.y;
      } else {
        // ROTATE SCENE
        rotation.current.y += dx * 0.01;
        rotation.current.x += dy * 0.01;
      }
    });

    // Zoom
    canvas.addEventListener('wheel', (e) => {
      e.preventDefault();
      const zoomSpeed = 0.5;
      camera.position.z += e.deltaY * 0.01 * zoomSpeed;
      camera.position.z = Math.max(1, Math.min(camera.position.z, 50)); // Clamp zoom
    });

    const animate = () => {
      requestAnimationFrame(animate);
      group.rotation.y = rotation.current.y;
      group.rotation.x = rotation.current.x;

      renderer.render(scene, camera);
      gl.endFrameEXP();
    };
    animate();
  };

  return (
    <View style={{ flex: 1 }}>
      <GLView
        style={{ flex: 1 }}
        onContextCreate={onContextCreate}
        webglContextAttributes={{ preserveDrawingBuffer: true }}
      />
    </View>
  );
}
