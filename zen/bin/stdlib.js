

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

var log = {
    __type: 'function',
    __call: function(x) { console.log(x.__value) }};

var call = {
    __type: 'function',
    __call: function(x) { return x.__call() }};


not = {"__type": "function", "__call": function (x) {
    if (__dispatch_method(x, ":as", Boolean).__value) {
        __gensym_5 = {"__type": "bool", "__value": false, "__class": Boolean};
    } else {
        __gensym_5 = {"__type": "bool", "__value": false, "__class": Boolean};
    };
    return __gensym_5;
}};
call = {"__type": "function", "__call": function (x) {
    return __dispatch(js_call, x);
}};
__gensym_6 = {"__type": "function", "__call": function (x, y) {
    return {"__type": "bool", "__value": x.__value == y.__value, "__class": Boolean};
}};
__gensym_7 = {"__type": "function", "__call": function (x, y) {
    return {"__type": "bool", "__value": x.__value != y.__value, "__class": Boolean};
}};


Boolean = (function () {
    var cls;
    var factory;
    cls = {"__type": "class", "__default_methods": {":as": function (self, Boolean) {
        return self;
    }, ":as": function (self, Integer) {
        if (__dispatch_method(self, ":as", Boolean).__value) {
            __gensym_8 = {"__type": "int", "__value": 1, "__class": Integer};
        } else {
            __gensym_8 = {"__type": "int", "__value": 0, "__class": Integer};
        };
        return __gensym_8;
    }, ":as": function (self, String) {
        if (__dispatch_method(self, ":as", Boolean).__value) {
            __gensym_9 = {"__type": "string", "__value": "true", "__class": String};
        } else {
            __gensym_9 = {"__type": "string", "__value": "false", "__class": String};
        };
        return __gensym_9;
    }}};
    factory = function () {
        return {"__type": "object", "__methods": {}, "__value": {}, "__class": cls};
    };
    cls.__new = factory;
    return cls;
})();
Integer = (function () {
    var cls;
    var factory;
    cls = {"__type": "class", "__default_methods": {":as": function (self, Integer) {
        return self;
    }, ":as": function (self, Boolean) {
        return __dispatch(__gensym_7, self, {"__type": "int", "__value": 0, "__class": Integer});
    }, ":as": function (self, String) {
        return __dispatch(js_int_to_string, self.__value);
    }}};
    factory = function () {
        return {"__type": "object", "__methods": {}, "__value": {}, "__class": cls};
    };
    cls.__new = factory;
    return cls;
})();
String = (function () {
    var cls;
    var factory;
    cls = {"__type": "class", "__default_methods": {":empty?": function (self) {
        return __dispatch(__gensym_6, __dispatch_method(self, ":length"), {"__type": "int", "__value": 0, "__class": Integer});
    }, ":length": function (self) {
        return __dispatch(js_int, self.__value.length);
    }, ":as": function (self, String) {
        return self;
    }, ":as": function (self, Boolean) {
        return __dispatch(not, __dispatch_method(self, ":empty?"));
    }, ":as": function (self, Integer) {
        return __dispatch(js_string_to_int, self.__value);
    }}};
    factory = function () {
        return {"__type": "object", "__methods": {}, "__value": {}, "__class": cls};
    };
    cls.__new = factory;
    return cls;
})();
Set = (function () {
    var cls;
    var factory;
    cls = {"__type": "class", "__default_methods": {":size": function (self) {
        return __dispatch(js_int, self.js_set.size);
    }, ":empty?": function (self) {
        return __dispatch(__gensym_6, __dispatch_method(self, ":size"), {"__type": "int", "__value": 0, "__class": Integer});
    }}};
    factory = function () {
        return {"__type": "object", "__methods": {}, "__value": {}, "__class": cls};
    };
    cls.__new = factory;
    return cls;
})();
print = {"__type": "function", "__call": function (x) {
    return __dispatch(js_log, __dispatch_method(x, ":as", String));
}};
