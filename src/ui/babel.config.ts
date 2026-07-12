// https://www.unistyl.es/v3/other/babel-plugin#extra-configuration

module.exports = function (api) {
  api.cache(true);

  return {
    presets: ["babel-preset-expo"],

    // other config
    plugins: [
      // other plugins
      [
        "react-native-unistyles/plugin",
        {
          // pass root folder of your application
          // all files under this folder will be processed by the Babel plugin
          // if you need to include more folders, or customize discovery process
          // check available babel options
          root: "src",
        },
      ],
    ],
  };
};
