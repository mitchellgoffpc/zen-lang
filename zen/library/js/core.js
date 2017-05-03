function __dispatch(f) {
    var args = Array.prototype.slice.call(arguments, 1);
    return f.__call.apply(null, args);
};

function __dispatch_method(obj, selector) {
    var args = Array.prototype.slice.call(2, arguments);
    args.unshift(obj);

    if (obj.__methods && obj.__methods[selector]) {
        return obj.__methods[selector].apply(null, args);
    } else {
        return obj.__class.__default_methods[selector].apply(null, args);
    }};

var __int = {
    __type: 'function',
    __call: function(x) {
        return {__type: 'int', __class: Integer, __value: x}
    }};

var __str = {
    __type: 'function',
    __call: function(x) {
        return {__type: 'str', __class: String, __value: x.toString()}
    }};

var __write_str = {
    __type: 'function',
    __call: function(x) {
        if (x.__type == 'tuple') {
            var contents = x.__value.map(function(x) { return __write_str.__call(x) });
            return '(' + contents.join(' ') + ')';
        } else if (x.__type == 'string') {
            return '"' + x.__value + '"'
        } else {
            return x.__value.toString();
        }}};

var __write = function(x) {
    console.log(__write_str.__call(x));
};

var print = {
    __type: 'function',
    __call: function(x) {
        var str = __dispatch_method(x, ':str');
        console.log(str.__value);
    }};

var call = {
    __type: 'function',
    __call: function(x) { return x.__call() }};
