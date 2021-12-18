import collections
from .CProtoParser import CProtoParser
from .util import expand_args, read_file, ListDelegator
import types
import os
import hashlib
import pytest


BuildSpec = collections.namedtuple("BuildSpec", "source_file,build_parameters")

_BuildResult = collections.namedtuple("BuildResult", "lib,source_file,build_dir,output,build_command,build_spec,functions")

class BuildResult(_BuildResult):

    def compute_built_filename(self, filename):
        return os.path.join(self.build_dir, filename)

    def extract_build_name(self, filename):
        _, source_name = os.path.split(self.source_file)
        source_name_base, _ = os.path.splitext(source_name)
        return source_name_base

    def get_default_function_name(self):
        if len(self.functions) == 1:
            return list(self.functions.values())[0].name
        else:
            raise ValueError(f"There's is not exactly one function ({list(self.functions.keys())}), so you need to provide one.")

def build(builder, build_spec):
    return builder.build(build_spec)

class Builder:
    
    def __init__(self, build_spec, build_root=None, parser=None, result_factory=None):
        self.build_spec = build_spec
        self.source_file = build_spec.source_file
        self.result_factory = result_factory or BuildResult
        self.parser = parser or CProtoParser()
        self.source_name_base = self._compute_source_name_base()
        self.build_parameters = build_spec.build_parameters
        self.build_root = build_root
        if self.build_root is None:
            self.build_root = os.environ.get("FIDDLE_BUILD_ROOT", "fiddle/builds")
        self.build_directory = self._compute_build_directory()

        
    def build(self):
        raise NotImplemented

    
    def _compute_build_directory(self):
        return os.path.join(self.build_root, "__".join([f"{p}_{v.replace(' ', '')}" for p,v in self.build_parameters.items()]) + "_" + self.source_name_base)

    
    def _compute_source_name_base(self):
        _, source_name = os.path.split(self.source_file)
        source_name_base, _ = os.path.splitext(source_name)
        return source_name_base

class BuildFailure(Exception):
    def __str__(self):
        return f"Build command failed:\n\n{self.args[0]}\n\n{self.args[1]}"
    
class BadBuildParameter(Exception):
    pass

    
    
class _Builder:
    
    def __init__(self, parser=None, build_root=None, analyses=None):
        self._source_file = None
        self.parser = parser or CProtoParser()
        self.analyses = analyses or {}
        self.build_root = build_root
        if self.build_root is None:
            self.build_root = os.environ.get("FIDDLE_BUILD_ROOT", "fiddle/builds")

    def build_one(self, parameters=None):
        raise NotImplemented

    
    def build(self, source_file=None, parameters=None, code=None, **kwargs):

        if source_file is None:
            if code is None:
                raise ValueError("You must provide either a source_file or code")
            source_file = self._write_anonymous_source(code)

        self._source_file = source_file

            
        if isinstance(source_file, BuildResult):
            source_file = source_file.source_file
        
        if code:
            self._update_source(source_file, code)

        if isinstance(parameters, list):
            singleton = False
        else:
            singleton = None
            
        if parameters is None:
            parameters = [] if kwargs else {}
            
        if isinstance(parameters, dict):
            parameters = [parameters]
        if kwargs:
            parameters += expand_args(**kwargs)

        if singleton is None:
            singleton = len(parameters) == 1

        self._raise_on_invalid_parameters(parameters)
        
        r = ListDelegator(self._add_analysis_functions(self.build_one(p)) for p in parameters)
        return r[0] if singleton else r

    
    def __call__(self, *argc, **kwargs):
        return self.build(*argc, **kwargs)

    
    def _raise_on_invalid_parameters(self, parameters):
        for p in parameters:
            for k,v in p.items():
                if not any([isinstance(v, t) for t in [int, str, float]]) or isinstance(v, bool): # bool is an int!
                    raise ValueError(f"Can't have '{v}' as parameter value in {p}")

                
    def _add_analysis_functions(self, result):
        for a in self.analyses:
            setattr(result, a, types.MethodType(self.analyses[a], result))
        return result

    
    def _update_source(self, source_file, source):
        if os.path.exists(source_file):
            with open(source_file) as r:
                contents = r.read()
        else:
            contents = None
            
        if contents != source:
            with open(source_file, "w") as r:
                r.write(source)

                
    def _write_anonymous_source(self, code):
        hash_value = hashlib.md5(code.encode('utf-8')).hexdigest()
        os.makedirs(self.build_root, exist_ok=True)
        anonymous_source_path = os.path.join(self.build_root, f"{hash_value}.cpp")
        with open(anonymous_source_path, "w") as f:
            f.write(code)
        return anonymous_source_path

    
    def _compute_build_directory(self, parameters):
        return os.path.join(self.build_root, "__".join([f"{p}_{v.replace(' ', '')}" for p,v in parameters.items()]) + "_" + self._source_name_base)


    def register_analysis(self, analysis, as_name=None):
        if as_name is None:
            as_name = analysis.__name__
        self.analyses[as_name] = analysis
        return self

    

            
class CompiledFunctionDelegator:
    def __init__(self, build_result, function_name=None):
        self.build_result = build_result
        if function_name is None:
            function_name = build_result.get_default_function_name()

        self.function_name = function_name

    def __getattr__(self, name):
        attr = getattr(self.build_result, name)
        if callable(attr):
            def redirect_to_build_result(*args, **kwargs):
                return attr(self.function_name, *args, **kwargs)
            return redirect_to_build_result
        else:
            return attr

    
def test_builder():

    simple_singleton = NopBuilder().build("test_src/test.cpp")
    assert isinstance(simple_singleton, BuildResult)
    assert simple_singleton.parameters == {}

    parameters = dict(foo="bar")

    singleton = NopBuilder().build("test_src/test.cpp", parameters)
    assert isinstance(singleton, BuildResult)
    assert singleton.parameters == parameters

    single_item_list = NopBuilder().build("test_src/test.cpp", parameters=[parameters])
    assert isinstance(single_item_list, list)
    assert len(single_item_list) == 1

    empty_list = NopBuilder().build("test_src/test.cpp", parameters=[])
    assert isinstance(empty_list, list)
    assert len(empty_list) == 0

    kwargs_singleton = NopBuilder().build("test_src/test.cpp", **parameters)
    assert isinstance(kwargs_singleton, BuildResult)
    assert kwargs_singleton.parameters == parameters

    short_list = NopBuilder().build("test_src/test.cpp", [parameters])
    assert isinstance(short_list, list)
    assert len(short_list) == 1
    assert short_list[0].parameters == parameters

    kwargs_list = NopBuilder().build("test_src/test.cpp", foo=["bar","baz"], bar="foo")
    assert isinstance(kwargs_list, list)
    assert len(kwargs_list) == 2
    assert all([isinstance(x, BuildResult) for x in kwargs_list])
    assert kwargs_list[0].parameters == dict(foo="bar", bar="foo")
    assert kwargs_list[1].parameters == dict(foo="baz", bar="foo")
    
    compound_list = NopBuilder()("test_src/test.cpp", parameters=[parameters, dict(b="c")], foo=["bar","baz"], bar="foo")
    assert isinstance(compound_list, list)
    assert len(compound_list) == 4
    assert all([isinstance(x, BuildResult) for x in compound_list])
    assert compound_list[0].parameters == parameters

    embedded_code = NopBuilder().build(code="somecode")
    assert os.path.exists(embedded_code.source_file)
    assert read_file(embedded_code.source_file) == "somecode"

def test_invalid_parameters():
    with pytest.raises(ValueError):
        singleton = NopBuilder().build("test_src/test.cpp", OPTIMIZE=None)
    with pytest.raises(ValueError):
        singleton = NopBuilder().build("test_src/test.cpp", OPTIMIZE=[None, ""])
    with pytest.raises(ValueError):
        singleton = NopBuilder().build("test_src/test.cpp", OPTIMIZE=[[], ""])
    with pytest.raises(ValueError):
        singleton = NopBuilder().build("test_src/test.cpp", OPTIMIZE=[True, ""])
    with pytest.raises(ValueError):
        singleton = NopBuilder().build("test_src/test.cpp", OPTIMIZE=[{}, ""])
    
def test_decoration():
    
    def get_parameters(build_result):
        return build_result.parameters

    def get_one_parameter(build_result, parameter):
        return build_result.parameters[parameter]

    build = NopBuilder()
    build.register_analysis(get_parameters)
    build.register_analysis(get_one_parameter)

    parameters = dict(foo="bar")
    singleton = build("test_src/test.cpp", parameters)
    assert singleton.get_parameters() == parameters
    assert singleton.get_one_parameter("foo") == "bar"

    
def test_delegator():
    build = NopBuilder()
    build.register_analysis(CompiledFunctionDelegator, as_name="function")
    def return_function(build_result, function_name):
        return build_result.functions[function_name]
    build.register_analysis(return_function)
    simple_singleton = build.build("test_src/test.cpp")

    delegated_function = simple_singleton.function("test_func")

    assert delegated_function.parameters == simple_singleton.parameters
    assert simple_singleton.functions["test_func"] == "nonsense_value"
    assert delegated_function.return_function() == "nonsense_value"

def test_embedded_source():
    from .MakeBuilder import build
    
    build.register_analysis(CompiledFunctionDelegator, as_name="function")

    if_ex = build(code=r"""
#include<cstdint>
#include<cstdlib>

extern "C" 
int if_ex(uint64_t array, unsigned long int size) {
	if (size == 0) {
		return NULL;
	}
	return array+size;
}
""")

    if_ex = if_ex.function()


def test_alternate_build_directory():
    from .util import environment
    import tempfile
    
    with tempfile.TemporaryDirectory() as d:
        build_root=os.path.join(d,"not_there")
        with environment(FIDDLE_BUILD_ROOT=build_root):
            build = NopBuilder()
            build(code="")
        assert os.path.exists(build_root)

            
