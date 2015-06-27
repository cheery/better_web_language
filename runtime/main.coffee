betterweb.main = () ->
    unless window?
        main_nodejs()

betterweb.load = (url, callback) ->
    req = new XMLHttpRequest()
    req.onload = () ->
        callback(req.response)
    req.responseType = 'json'
    req.open('get', url, true)
    req.send()

main_nodejs = () ->
    fs = require 'fs'
    load = (path) ->
        data = JSON.parse fs.readFileSync(path, encoding='utf8')
        console.log data

    for arg in process.argv[2...]
        arg += '.bc' unless arg.match(/.bc$/)
        load(arg)
