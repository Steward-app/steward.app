const path = require('path');
const {InjectManifest} = require('workbox-webpack-plugin');


module.exports = [
  {
    entry: './src/app.js',
    output: {
      filename: 'app.js',
      path: path.resolve(__dirname, 'static'),
      publicPath: 'static/',
    },
    module: {
      rules: [
        {
          test: /\.css$/i,
          use: ['style-loader', 'css-loader']
        }
      ]
    },
    plugins: [
      new InjectManifest({
        swSrc: './src/sw.js',
      })
    ],
  },
  {
    entry: './src/sw.js',
    output: {
      filename: 'sw.js',
      path: path.resolve(__dirname, 'static'),
    },
  },
];
