betterweb.main = () ->
    unless window?
        main_nodejs()

betterweb.load = (url, callback) ->
    req = new XMLHttpRequest()
    req.onload = () ->
        callback(betterweb.load_from_arraybuffer(req.response))
    req.responseType = 'arraybuffer'
    req.open('get', url, true)
    req.send()

betterweb.load_from_arraybuffer = (data) ->
    # Later this should return a callable,
    # which produces a module object.
    betterweb.evaluate(data)

main_nodejs = () ->
    fs = require 'fs'
    for arg in process.argv[2...]
        arg += '.bc' unless arg.match(/.bc$/)
        data = to_arraybuffer(fs.readFileSync(arg))
        betterweb.load_from_arraybuffer(data)

to_arraybuffer = (buffer) ->
    ab = new ArrayBuffer(buffer.length)
    view = new Uint8Array(ab)
    view[i] = buffer[i] for i in [0...buffer.length]
    return ab
