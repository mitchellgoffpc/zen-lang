function __dispatch(f) {
    var args = Array.prototype.slice.call(arguments, 1);

    if (f.__type == 'class') {
        var obj = f.__create();
        if (f.__init) {
            f.__init.apply(null, [obj].concat(args));
        }
        return obj;
    } else {
        return f.__call.apply(null, args);
    }};

function __dispatch_method(obj, selector) {
    var args = Array.prototype.slice.call(arguments, 2);
    args = [obj, null].concat(args);

    var _name = obj.__class.__name;
    var _methods = obj.__class.__methods;
    var _super = obj.__class.__super;

    if (_methods && _methods[selector]) {
        return _methods[selector].apply(null, args);
    } else if (_super && _super.__methods && _super.__methods[selector]) {
        return _super.__methods[selector].apply(null, args);
    } else {
        console.log(obj.__class);
        throw Error(`(class ${_name}) doesn't know how to respond to selector (${selector})`);
    }};

var __bool = {
    __type: 'function',
    __call: function(x) {
        return {__type: 'bool', __class: #{Bool}, __value: (x ? true : false)};
    }};

var __int = {
    __type: 'function',
    __call: function(x) {
        return {__type: 'int', __class: #{Int}, __value: x};
    }};

var __str = {
    __type: 'function',
    __call: function(x) {
        return {__type: 'str', __class: #{String}, __value: x.toString()};
    }};

var __new = {
    __type: 'function',
    __call: function(x) {
        var args = Array.prototype.slice.call(arguments, 1);
        return new (Function.prototype.bind.apply(x, args));
    }};

var __class = {
    __type: 'function',
    __call: function(x) { return x.__class }}

var __write_str = {
    __type: 'function',
    __call: function(x) {
        if (x.__class == #{Tuple}) {
            var contents = x.__value.map(function(x) { return __write_str.__call(x).__value });
            return __str.__call('(' + contents.join(' ') + ')');
        } else if (x.__class == #{String}) {
            return __str.__call('"' + x.__value + '"');
        } else {
            return __str.__call(x.__value.toString());
        }}};

var __write = function(x) {
    console.log(__write_str.__call(x).__value);
};

var log = {
    __type: 'function',
    __call: function(x) { console.log(x.__value) }};

var call = {
    __type: 'function',
    __call: function(x) { return x.__call() }};

var index = {
    __type: 'function',
    __call: function(x, y) { return x[y] }}

var is_type = {
    __type: 'function',
    __call: function(x, y) { return __bool.__call(x.__class == y) }};

var int_to_string = {
    __type: 'function',
    __call: function(x) { return __str.__call(x.toString()) }};
