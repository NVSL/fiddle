#-*- Makefile -*-

BUILD=build

CXX?=g++
CC?=gcc
WARNINGS=-Wall -Werror
DEBUG_FLAGS=-g 
INCLUDES=-I. -I$(FIDDLE_INCLUDE)
CFLAGS=$(WARNINGS) $(DEBUG_FLAGS) -fPIC $(OPTIMIZE) $(INCLUDES) $(MORE_INCLUDES) $(MORE_CFLAGS) -MMD -save-temps=obj
CXXFLAGS=$(CFLAGS) $(CXX_STANDARD) $(MORE_CXXFLAGS)
CXX_STANDARD=-std=gnu++11

LDFLAGS=$(LD_OPTS) $(MORE_LDFLAGS) #-pthread  #-std=gnu++11  

.PRECIOUS: $(BUILD)/%.o  $(BUILD)/%.s $(BUILD)%.ii
.PHONY: default
default:

MORE_OBJS=$(addprefix $(BUILD)/,$(addsuffix .o, $(basename $(MORE_SRC))))

$(BUILD)/%.o : %.cpp
	@mkdir -p $(BUILD)
	$(CXX) -c $(CXXFLAGS) $< -o $@

$(BUILD)/%.o : %.CPP
	@mkdir -p $(BUILD)
	$(CXX) -c $(CXXFLAGS) $< -o $@

$(BUILD)/%.o : %.cp
	@mkdir -p $(BUILD)
	$(CXX) -c $(CXXFLAGS) $< -o $@

$(BUILD)/%.o : %.cc
	@mkdir -p $(BUILD)
	$(CXX) -c $(CXXFLAGS) $< -o $@

$(BUILD)/%.o : %.cxx
	@mkdir -p $(BUILD)
	$(CXX) -c $(CXXFLAGS) $< -o $@

$(BUILD)/%.o : %.C
	@mkdir -p $(BUILD)
	$(CXX) -c $(CXXFLAGS) $< -o $@

$(BUILD)/%.o : %.c++
	@mkdir -p $(BUILD)
	$(CXX) -c $(CXXFLAGS) $< -o $@

$(BUILD)/%.o : %.c
	@mkdir -p $(BUILD)
	$(CC) -c $(CXXFLAGS) $< -o $@

$(BUILD)/%.so: $(BUILD)/%.o  $(MORE_OBJS)
	@mkdir -p $(BUILD)
	$(CXX) $^ $(LDFLAGS) -shared -o $@


-include $(wildcard *.d) $(wildcard $(BUILD)/*.d)
.PHONY: fiddle-clean
fiddle-clean:
	rm -rf $(BUILD)

clean: fiddle-clean

.PHONY: help

help:
	@echo 'make clean     : cleanup'

