const path = require('path');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');

module.exports = [
  {
    entry: './src/app.js',
    output: {
      filename: 'app.js',
      path: path.resolve(__dirname, 'static'),
    },
    module: {
      rules: [
        {
          test: /\.css$/i,
          use: ['style-loader', 'css-loader']
        }
      ]
    }
  },
  {
    entry: './src/sw.js',
    output: {
      filename: 'sw.js',
      path: path.resolve(__dirname, 'static'),
    },
  },
];
