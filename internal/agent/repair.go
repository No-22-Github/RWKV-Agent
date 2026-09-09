package agent

import "github.com/no22/RWKV-Agent/internal/agent/wire"

// repairLog collects de-duplicated repair IDs in first-seen order. The parser
// reports what it had to fix, not just that it fixed something.
type repairLog struct {
	seen    map[wire.Repair]struct{}
	repairs []wire.Repair
}

func (log *repairLog) mark(repair wire.Repair) {
	if log.seen == nil {
		log.seen = make(map[wire.Repair]struct{}, 4)
	}
	if _, exists := log.seen[repair]; exists {
		return
	}
	log.seen[repair] = struct{}{}
	log.repairs = append(log.repairs, repair)
}

func (log *repairLog) list() []wire.Repair {
	if len(log.repairs) == 0 {
		return nil
	}
	return log.repairs
}

func (log *repairLog) any() bool { return len(log.repairs) > 0 }
