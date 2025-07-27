import React, { useRef, useEffect, useState } from 'react';
import { View } from 'react-native';
import { GLView } from 'expo-gl';
import { Renderer } from 'expo-three';
import * as THREE from 'three';

import { QuadData } from '@/interfaces/messages';

interface Plot3DProps {
  hexData?: QuadData;
}

export default function Plot3D({ quadData }: Plot3DProps) {

  const isDragging = useRef(false);
  const lastMousePosition = useRef({ x: 0, y: 0 });
  const rotation = useRef({ x: 0, y: 0 });
  const pan = useRef({ x: 0, y: 0 });
  const cameraRef = useRef();
  const groupRef = useRef();

  const points = [
    new THREE.Vector3(0, 0, 0),
    new THREE.Vector3(1, 1, 0),
    new THREE.Vector3(2, 0, 1),
    new THREE.Vector3(1, -1, 0),
  ];


    const lastUpdateRef = useRef<number>(0);
  const [throttledPlotData, setThrottledPlotData] = useState<any[]>([]);


  useEffect(() => {
    if (quadData) {
      if (hold) return;
      if (Date.now() - lastUpdateRef.current > max_plot_refresh_rate_ms) {
        lastUpdateRef.current = Date.now();
        setThrottledPlotData(computePlotData(quadData));
      }
    }
  }, [quadData]);

  const onContextCreate = async (gl) => {
    const { drawingBufferWidth: width, drawingBufferHeight: height } = gl;

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(75, width / height, 0.1, 1000);
    camera.position.set(0, 0, 5);
    cameraRef.current = camera;

    const renderer = new Renderer({ gl });
    renderer.setSize(width, height);
    renderer.setClearColor(0x000000, 1);

    const group = new THREE.Group();
    groupRef.current = group;

    // Add points
    const pointMaterial = new THREE.PointsMaterial({ color: 0xff0000, size: 0.1 });
    const pointGeometry = new THREE.BufferGeometry().setFromPoints(points);
    const pointCloud = new THREE.Points(pointGeometry, pointMaterial);
    group.add(pointCloud);

    // Add lines
    const lineMaterial = new THREE.LineBasicMaterial({ color: 0x00ff00 });
    const lineGeometry = new THREE.BufferGeometry().setFromPoints(points);
    const line = new THREE.Line(lineGeometry, lineMaterial);
    group.add(line);

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
