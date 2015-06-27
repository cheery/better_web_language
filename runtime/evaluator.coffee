betterweb.evaluate = (data, pc=0) ->
    header = new Uint32Array(data, 0, 1)
    regs = []
    regs.length = header[0]
    u8 = new Uint8Array(data, 4)
    view = new DataView(data, 4)
    while true
        switch u8[pc]
            when 1
                regs[u8[pc+1]] = view.getInt32(pc+2, true)
                pc += 6
            when 2
                console.log regs[u8[pc+1]]
                pc += 2
            when 3
                return regs[u8[pc+1]]
            else
                throw "unknown instruction: #{u8[pc]}"
