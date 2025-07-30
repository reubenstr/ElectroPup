import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

type VerticalTextProps = {
  text: string;
  style?: object;
};

export const VerticalText: React.FC<VerticalTextProps> = ({ text, style }) => {
  return (
    <View style={[styles.wrapper, style]}>
      <Text style={styles.rotatedText}>{text}</Text>
    </View>
  );
};

const styles = StyleSheet.create({
  wrapper: {
    height: 100,
    width: 100,
    justifyContent: 'center',
    alignItems: 'flex-start',
    overflow: 'visible',
  },
  rotatedText: {
    transform: [{ rotate: '-90deg' }],
    fontSize: 12,
    color: 'black',
    textAlign: 'left',
    width: 100, // This becomes the height after rotation
  },
});
