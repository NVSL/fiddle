from .util import get_native_architecture
import re
import copy
import collections

class ToolchainRegistry:
    def __init__(self):
        self._toolchains = []
        
    def register_toolchain(self, tool_regex, languages, tc_type):
        self._toolchains.append((tool_regex, list(map(lambda x: x.upper(), languages)), tc_type))

    def get_toolchain(self, language, build_parameters, tool):

        for pattern, languages, tc_type  in self._toolchains:
            if re.match(pattern, tool):
                print(pattern)
                print(tool)

                if language.upper() in languages:
                    return tc_type(language, build_parameters)

        raise UnknownToolchain(f"Toolchain for '{tool}' is not recognized.")


TheToolchainRegistry = ToolchainRegistry()    


class UnknownToolchain(Exception):
    pass


class Toolchain:
    pass


class GCCToolchain(Toolchain):

    _gcc_architectures = collections.OrderedDict()

    @classmethod
    def register_gcc_architecture(cls, architectures, toolchain_prefix):
        for a in architectures:
            cls._gcc_architectures[a.upper()] = toolchain_prefix

    
    def __init__(self, language, build_parameters):
        
        self._language = language.upper()
        self._build_parameters = copy.copy(build_parameters)
        
        self._set_compiler_and_architecture()
        
        self._set_architecture_specific_parameters()

        
    def update_suffix_for_native(self):
        if self.architecture_name == get_native_architecture():
            self._tool_prefix = ""

    def get_asm_function_bookends(self, function):
        return self._asm_function_bookends(function)

    def get_compiler(self):
        return self._compiler
    
    def get_tool(self, tool):
        return f"{self._tool_prefix}{tool}"

    def describe(self):
        return f"{self._tool_prefix}gcc toolchain compiling for {self._architecture_name}"

    def _set_compiler_and_architecture(self):

        if self._language == "C":
            self._compiler = self._build_parameters.get("CC", "gcc")
        elif  self._language == "C++":
            self._compiler = self._build_parameters.get("CXX", "g++")
        else:
            raise Exception(f"Unknown language for this toolchain: {language}")
            
        if "ARCH" in self._build_parameters:

            arch = self._build_parameters['ARCH']
            try:
                prefix = GCCToolchain._gcc_architectures[arch.upper()]
                if prefix != "":
                    prefix += "-"
                    
                self._compiler = f"{prefix}{self._compiler}"
            except KeyError:
                raise UnknownToolchain(f"No known toolchain for architecture '{arch}'.")

        self._tool_prefix, self._compiler_suffix = self._parse_executable_name(self._compiler)

        self._architecture_name = self._convert_tool_prefix_to_architecture(self._tool_prefix)

    def _parse_executable_name(self, name):
        parts = name.split("-")
        if len(parts) in [1,2]:  # e.g. 'gcc' or 'gcc-9
            return "", "-".join(parts)
        elif len(parts) in [4,5]:  # e.g. 'arm-linux-gnu-gcc' or 'arm-linux-gnu-gcc-9'
            return "-".join(parts[:3])+"-", "-".join(parts[3:])
        else:
            raise UnknownToolchain(f"Couldn't deduce compiler architecture and version from compiler '{name}'")

    def _convert_tool_prefix_to_architecture(self, prefix ):
        for name, tool_prefix in GCCToolchain._gcc_architectures.items():
            if tool_prefix == prefix:
                return name
        # make a guess...
        return prefix.split("-")[0]

    def _set_architecture_specific_parameters(self):
        if self._architecture_name == "aarch64" or "arm" in self._architecture_name:
            self._asm_function_bookends = lambda function: (fr"^{re.escape(function)}:\s*", ".fnend")
        else:
            self._asm_function_bookends = lambda function: (fr"^{re.escape(function)}:\s*", ".cfi_endproc")
            

class GoToolchain(Toolchain):

    # Go cross compilation: https://stackoverflow.com/questions/32557438/how-do-i-cross-compile-my-go-program-from-mac-os-x-to-ubuntu-64-bit
    # and here https://stackoverflow.com/questions/23377271/how-do-i-cross-compile-a-go-program-on-a-mac-for-ubuntu
    # and here https://dave.cheney.net/2015/03/03/cross-compilation-just-got-a-whole-lot-better-in-go-1-5
    def __init__(self, language, build_parameters):
        self._bintools_delegate = TheToolchainRegistry.get_toolchain("C", build_parameters, "gcc")
        
    def get_asm_function_bookends(self, function):
        return self._bintools_delegate.get_asm_function_bookends(function)

    def get_compiler(self):
        return "go"
    
    def describe(self):
        return f"Go toolchain compiling for NATIVE"

# The "official" architecture name form os.uname().machine should go first in the list of names
GCCToolchain.register_gcc_architecture(["aarch64", "arm"], "arm-linux-gnueabi")
GCCToolchain.register_gcc_architecture(["x86_64", "x86"], "x86_64-linux-gnu")
GCCToolchain.register_gcc_architecture(["ppc64", "ppc", "powerpc"], "powerpc-linux-gnu")
GCCToolchain.register_gcc_architecture(["native"], "")

TheToolchainRegistry.register_toolchain(tool_regex=r"(\w+-\w+-\w+-)?(gcc|g\+\+)(-\d+)?", languages=["C++", "C"], tc_type=GCCToolchain)
TheToolchainRegistry.register_toolchain(tool_regex=r"go", languages=["GO"], tc_type=GoToolchain)



