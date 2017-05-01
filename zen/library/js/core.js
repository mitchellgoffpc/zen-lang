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

var print = {
    __type: 'function',
    __call: function(x) {
        var str = __dispatch_method(x, ':str');
        console.log(str.__value);
    }};
