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
    view = new DataView(data, 0)
    function_count = view.getUint32(0, true)
    functions = []
    offset = 4
    for function_id in [0...function_count]
        length = view.getUint32(offset, true)
        regc   = view.getUint32(offset+4, true)
        func_data = data.slice(offset+8, offset+8+length)
        offset += 8+length
        functions.push {regc, data:func_data}

    # Later this should return a callable,
    # which produces a module object.
    betterweb.evaluate(functions, functions[0])

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
