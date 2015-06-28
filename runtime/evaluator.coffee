betterweb.evaluate = (data, pc=0) ->
    globals = {
        'print': (args...) ->
            console.log args...
    }
    header = new Uint32Array(data, 0, 1)
    regs = []
    regs.length = header[0]
    u8 = new Uint8Array(data, 4)
    view = new DataView(data, 4)
    while true
        switch u8[pc]
            when 1 #int32
                regs[u8[pc+1]] = view.getInt32(pc+2, true)
                pc += 6
            when 2 #string
                length = view.getUint16(pc+2, true)
                regs[u8[pc+1]] = betterweb.utf8ToString(u8, pc+4, pc+4+length)
                pc += 4 + length
            when 3 #return
                return regs[u8[pc+1]]
            when 4 #getglobal
                length = view.getUint16(pc+2, true)
                string = betterweb.utf8ToString(u8, pc+4, pc+4+length)
                if globals[string] == undefined
                    throw "#{string} not in global scope"
                regs[u8[pc+1]] = globals[string]
                pc += 4 + length
            when 5 #call
                argc = view.getUint16(pc+3, true)
                argv = for i in [0...argc]
                    regs[u8[pc+5+i]]
                regs[u8[pc+1]] = regs[u8[pc+2]].apply(null, argv)
                pc += 5+argc
            else
                throw "unknown instruction: #{u8[pc]}"
