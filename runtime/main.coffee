fs = require 'fs'

betterweb.main = () ->
    for arg in process.argv[2...]
        arg += '.bc' unless arg.match(/.bc$/)
        betterweb.load(arg)

betterweb.load = (path) ->
    data = JSON.parse fs.readFileSync(path, encoding='utf8')
    console.log data
