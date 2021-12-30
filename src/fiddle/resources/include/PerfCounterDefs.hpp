

#ifndef PERF_COUNTER_DEFS_INCLUDED
#define PERF_COUNTER_DEFS_INCLUDED

#define PERF_HW_COUNTERS					  \
	HW_COUNTER(CPU_CYCLES)				  \
	HW_COUNTER(INSTRUCTIONS)				  \
	HW_COUNTER(CACHE_REFERENCES)			  \
	HW_COUNTER(CACHE_MISSES)				  \
	HW_COUNTER(BRANCH_INSTRUCTIONS)			  \
	HW_COUNTER(BRANCH_MISSES)				  \
	HW_COUNTER(BUS_CYCLES)				  \
	HW_COUNTER(STALLED_CYCLES_FRONTEND)		  \
	HW_COUNTER(STALLED_CYCLES_BACKEND)			  \
	HW_COUNTER(REF_CPU_CYCLES)				  

#define PERF_SW_COUNTERS					  \
	SW_COUNTER(CPU_CLOCK)				  \
	SW_COUNTER(TASK_CLOCK)				  \
	SW_COUNTER(PAGE_FAULTS)				  \
	SW_COUNTER(CONTEXT_SWITCHES)			  \
	SW_COUNTER(CPU_MIGRATIONS)				  \
	SW_COUNTER(PAGE_FAULTS_MIN)			  \
	SW_COUNTER(PAGE_FAULTS_MAJ)			  \
	SW_COUNTER(ALIGNMENT_FAULTS)			  \
	SW_COUNTER(EMULATION_FAULTS)			  \
	SW_COUNTER(DUMMY)

#define PERF_CACHES		  \
	CACHE(L1D)			  \
	CACHE(L1I)			  \
	CACHE(LL)			  \
	CACHE(DTLB)		  \
	CACHE(ITLB)		  \
	CACHE(BPU)			  \
	CACHE(NODE)		  \
	CACHE(L1D)			  \
	CACHE(L1I)			  \
	CACHE(LL)			  \
	CACHE(DTLB)		  \
	CACHE(ITLB)		  \
	CACHE(BPU)			  \
	CACHE(NODE)

#define PERF_CACHE_OPS			\
	CACHE_OP(READ)				\
	CACHE_OP(WRITE)				\
	CACHE_OP(PREFETCH)

#define PERF_CACHE_RESULTS			\
	CACHE_RESULT(ACCESS)			\
	CACHE_RESULT(MISS)
	
#endif
