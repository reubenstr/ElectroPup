import React, { useState, useRef } from 'react';
import { View, Text, StyleSheet, Pressable } from 'react-native';

interface TooltipProps {
  label: string;
  value: string;
  children: React.ReactNode;
}

const MotorTooltip = ({ label, value, children }: TooltipProps) => {
  const [visible, setVisible] = useState(false);

  // Create refs to track the Pressable and tooltip container
  const tooltipRef = useRef<View | null>(null);
  const pressableRef = useRef<View | null>(null);

  // Handle mouse entering the element
  const handleMouseEnter = () => {
    setVisible(true); // Show the tooltip immediately
  };

  // Handle mouse leaving the element
  const handleMouseLeave = (e: React.MouseEvent) => {
    const relatedTarget = e.relatedTarget as HTMLElement;
    if (
      pressableRef.current?.contains(relatedTarget) || // Mouse entered Pressable
      tooltipRef.current?.contains(relatedTarget) // Mouse entered tooltip
    ) {
      return; // Don't hide tooltip if mouse is still inside Pressable or tooltip
    }

    // Hide tooltip immediately when mouse leaves both elements
    setVisible(false);
  };

  return (
    <View style={styles.wrapper}>
      <Pressable
        ref={pressableRef}
        onMouseEnter={handleMouseEnter}
        onMouseLeave={handleMouseLeave}
      >
        {children}
      </Pressable>
      {visible && (
        <View
          ref={tooltipRef}
          style={styles.tooltip}
          onMouseEnter={handleMouseEnter} // Keep visible when mouse enters tooltip
          onMouseLeave={handleMouseLeave} // Hide immediately when mouse leaves tooltip
        >
          <Text style={styles.label}>{label}</Text>
          <Text>{value}</Text>
        </View>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  wrapper: {
    position: 'relative',
  },
  tooltip: {
    position: 'absolute',
    top: -40,
    left: 0,
    padding: 8,
    backgroundColor: 'black',
    borderRadius: 4,
    zIndex: 9999,
    maxWidth: 200,
  },
  label: {
    fontWeight: 'bold',
    marginBottom: 2,
    color: 'white',
  },
});

export default MotorTooltip;
