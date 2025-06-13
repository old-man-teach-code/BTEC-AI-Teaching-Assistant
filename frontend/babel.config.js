module.exports = {
  presets: [
    ['@vue/cli-plugin-babel/preset', { requireConfigFile: false }],
    ['@babel/preset-env', { requireConfigFile: false }],
  ],
  // Ensure Babel does not look for a config file
  babelrc: false,
  configFile: false
};
