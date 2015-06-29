betterweb.evaluate = (functions, func, pc=0) ->
    globals = {
        'print': (args...) ->
            console.log args...
    }
    link = null
    regs = []
    regs.length = func.regc
    u8 = new Uint8Array(func.data)
    view = new DataView(func.data)
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
                retval = regs[u8[pc+1]]
                if link?
                    {dst, functions, link, pc, regs, u8, view} = link
                    regs[dst] = retval
                else
                    return retval
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
                callee = regs[u8[pc+2]]
                dst = u8[pc+1]
                pc += 5+argc
                if callee._actual_betterweb_handle?
                    link = {dst, functions, link, pc, regs, u8, view}
                    {functions, func} = callee._actual_betterweb_handle
                    regs = []
                    regs.length = func.regc
                    u8 = new Uint8Array(func.data)
                    view = new DataView(func.data)
                    pc = 0
                else
                    regs[dst] = callee.apply(null, argv)
            when 6 #setglobal
                length = view.getUint16(pc+1, true)
                string = betterweb.utf8ToString(u8, pc+3, pc+3+length)
                globals[string] = regs[u8[pc+3+length]]
                pc += 4+length
            when 7 #closure
                function_id = view.getUint16(pc+2, true)
                regs[u8[pc+1]] = make_closure(functions, function_id)
                pc += 4
            else
                throw "unknown instruction: #{u8[pc]}"

make_closure = (functions, function_id) ->
    func = functions[function_id]
    closure_handle = () ->
        betterweb.evaluate(functions, func)
    # Explicit link chain is used to implement greenlets/coroutines
    closure_handle._actual_betterweb_handle = {functions, func}
    return closure_handle
