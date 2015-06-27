fs = require 'fs'

betterweb.main = () ->
    for arg in process.argv[2...]
        arg += '.bc' unless arg.match(/.bc$/)
        console.log arg
