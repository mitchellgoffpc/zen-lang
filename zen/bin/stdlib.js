

function __dispatch(f) {
    var args = Array.prototype.slice.call(arguments, 1);

    if (f.__type == 'class') {
        var obj = f.__new();
        f.__init.apply(null, [obj].concat(args));
        return obj;
    } else {
        return f.__call.apply(null, args);
    }};

function __dispatch_method(obj, selector) {
    var args = Array.prototype.slice.call(arguments, 2);
    args = [obj, null].concat(args);

    var _methods = obj.__class.__methods;
    var _super = obj.__class.__super;

    if (_methods && _methods[selector]) {
        return _methods[selector].apply(null, args);
    } else if (_super && _super.__methods && _super.__methods[selector]) {
        return _super.__methods[selector].apply(null, args);
    } else {
        throw Error("(class " + name + ") doesn't know how to respond to selector " + selector);
    }};

var __bool = {
    __type: 'function',
    __call: function(x) {
        return {__type: 'bool', __class: bool, __value: (x ? true : false)};
    }};

var __int = {
    __type: 'function',
    __call: function(x) {
        return {__type: 'int', __class: int, __value: x};
    }};

var __str = {
    __type: 'function',
    __call: function(x) {
        return {__type: 'str', __class: str, __value: x.toString()};
    }};

var __new = {
    __type: 'function',
    __call: function(x) {
        var args = Array.prototype.slice.call(arguments, 1);
        return new (Function.prototype.bind.apply(x, args));
    }};

var __write_str = {
    __type: 'function',
    __call: function(x) {
        if (x.__type == 'tuple') {
            var contents = x.__value.map(function(x) { return __write_str.__call(x).__value });
            return __str.__call('(' + contents.join(' ') + ')');
        } else if (x.__type == 'string') {
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

var is_type = {
    __type: 'function',
    __call: function(x, y) { return __bool.__call(x.__class == y) }};

var int_to_string = {
    __type: 'function',
    __call: function(x) { return __str.__call(x.toString()) }};






__gensym_18 = {
    "__type": "function", 
    "__call": function () {
        if (true && true && true) {
            x = arguments[0];
            y = arguments[1];
            return {
                "__type": "bool", 
                "__value": x.__value == y.__value, 
                "__class": bool};
        } else {
            throw Error("Condition fell through");
        }}};
__gensym_19 = {
    "__type": "function", 
    "__call": function () {
        if (true && true && true) {
            x = arguments[0];
            y = arguments[1];
            return {
                "__type": "bool", 
                "__value": x.__value != y.__value, 
                "__class": bool};
        } else {
            throw Error("Condition fell through");
        }}};


__gensym_21 = {
    "__type": "function", 
    "__call": function () {
        if (true && true) {
            x = arguments[0];
            if (__dispatch(bool, x).__value) {
                __gensym_20 = {
                    "__type": "bool", 
                    "__value": true, 
                    "__class": bool};
            } else {
                __gensym_20 = {
                    "__type": "bool", 
                    "__value": true, 
                    "__class": bool};
            };
            return __gensym_20;
        } else {
            throw Error("Condition fell through");
        }}};
__gensym_22 = {
    "__type": "function", 
    "__call": function () {
        if (true && true) {
            x = arguments[0];
            return __dispatch(call, x);
        } else {
            throw Error("Condition fell through");
        }}};


__gensym_23 = (function () {
    var cls;
    var __new;
    cls = {
        "__type": "class", 
        "__name": "__gensym_23", 
        "__init": function (_self) {
            if (__dispatch(is_type, arguments[1], bool).__value && true) {
                value = arguments[1];
                return _self.__value = value.__value;
            } else if (__dispatch(is_type, arguments[1], int).__value && true) {
                value = arguments[1];
                if (__dispatch(bool, value).__value) {
                    __gensym_24 = {
                        "__type": "bool", 
                        "__value": true, 
                        "__class": bool};
                } else {
                    __gensym_24 = {
                        "__type": "bool", 
                        "__value": true, 
                        "__class": bool};
                };
                return (_self.__class.__init)(_self, __gensym_24);
            } else if (__dispatch(is_type, arguments[1], str).__value && true) {
                value = arguments[1];
                return (_self.__class.__init)(_self, __dispatch(__gensym_21, __dispatch_method(value, ":empty?")));
            } else {
                throw Error("Condition fell through");
            }}, 
        "__methods": {}};
    __new = function () {
        return {
            "__type": "object", 
            "__class": cls, 
            "__properties": {}};
    };
    cls.__new = __new;
    return cls;
})();
__gensym_25 = (function () {
    var cls;
    var __new;
    cls = {
        "__type": "class", 
        "__name": "__gensym_25", 
        "__init": function (_self) {
            if (__dispatch(is_type, arguments[1], bool).__value && true) {
                value = arguments[1];
                if (__dispatch(bool, _self).__value) {
                    __gensym_26 = {
                        "__type": "int", 
                        "__value": 1, 
                        "__class": int};
                } else {
                    __gensym_26 = {
                        "__type": "int", 
                        "__value": 0, 
                        "__class": int};
                };
                return (_self.__class.__init)(_self, __gensym_26);
            } else if (__dispatch(is_type, arguments[1], int).__value && true) {
                value = arguments[1];
                return __dispatch(__gensym_18, _self.__value, value.__value);
            } else if (__dispatch(is_type, arguments[1], str).__value && true) {
                value = arguments[1];
                return (_self.__class.__init)(_self, __dispatch(string_to_int, _self.__value));
            } else {
                throw Error("Condition fell through");
            }}, 
        "__methods": {}};
    __new = function () {
        return {
            "__type": "object", 
            "__class": cls, 
            "__properties": {}};
    };
    cls.__new = __new;
    return cls;
})();
__gensym_27 = (function () {
    var cls;
    var __new;
    cls = {
        "__type": "class", 
        "__name": "__gensym_27", 
        "__init": function (_self) {
            if (__dispatch(is_type, arguments[1], bool).__value && true) {
                value = arguments[1];
                if (__dispatch(bool, value).__value) {
                    __gensym_28 = {
                        "__type": "string", 
                        "__value": "true", 
                        "__class": str};
                } else {
                    __gensym_28 = {
                        "__type": "string", 
                        "__value": "false", 
                        "__class": str};
                };
                return (_self.__class.__init)(_self, __gensym_28);
            } else if (__dispatch(is_type, arguments[1], int).__value && true) {
                value = arguments[1];
                return (_self.__class.__init)(_self, __dispatch(int_to_string, value.__value));
            } else if (__dispatch(is_type, arguments[1], str).__value && true) {
                value = arguments[1];
                return _self.__value = value.__value;
            } else {
                throw Error("Condition fell through");
            }}, 
        "__methods": {
            ":empty?": function (_self) {
                if (true) {
                    return __dispatch(__gensym_18, __dispatch_method(_self, ":length"), {
                        "__type": "int", 
                        "__value": 0, 
                        "__class": int});
                } else {
                    throw Error("Condition fell through");
                }}, 
            ":length": function (_self) {
                if (true) {
                    return __dispatch(__int, _self.__value.length);
                } else {
                    throw Error("Condition fell through");
                }}}};
    __new = function () {
        return {
            "__type": "object", 
            "__class": cls, 
            "__properties": {}};
    };
    cls.__new = __new;
    return cls;
})();
__gensym_29 = (function () {
    var cls;
    var __new;
    cls = {
        "__type": "class", 
        "__name": "__gensym_29", 
        "__methods": {}};
    __new = function () {
        return {
            "__type": "object", 
            "__class": cls, 
            "__properties": {}};
    };
    cls.__new = __new;
    return cls;
})();
__gensym_30 = (function () {
    var cls;
    var __new;
    cls = {
        "__type": "class", 
        "__name": "__gensym_30", 
        "__methods": {}};
    __new = function () {
        return {
            "__type": "object", 
            "__class": cls, 
            "__properties": {}};
    };
    cls.__new = __new;
    return cls;
})();
__gensym_31 = {
    "__type": "function", 
    "__call": function () {
        if (true && true) {
            x = arguments[0];
            return __dispatch(log, __dispatch(str, x));
        } else {
            throw Error("Condition fell through");
        }}};
bool = __gensym_23;
int = __gensym_25;
str = __gensym_27;
array = __gensym_29;
