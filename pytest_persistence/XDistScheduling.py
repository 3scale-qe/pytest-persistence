from xdist.scheduler import LoadScheduling


class XDistScheduling(LoadScheduling):

    def __init__(self, config, log, test_order):
        super().__init__(config, log)
        self.test_order = test_order

    def schedule(self):
        assert self.collection_is_completed

        # Initial distribution already happened, reschedule on all nodes
        if self.collection is not None:
            for node in self.nodes:
                self.check_schedule(node)
            return

        # XXX allow nodes to have different collections
        if not self._check_nodes_have_same_collection():
            self.log("**Different tests collected, aborting run**")
            return

        # Collections are identical, create the index of pending items.
        self.collection = list(self.node2collection.values())[0]
        self.pending[:] = range(len(self.collection))
        if not self.collection:
            return

        if self.maxschedchunk is None:
            self.maxschedchunk = len(self.collection)

        for (test, gw) in self.test_order.items():
            node = [x for x in self.nodes if x.gateway.id == gw][0]
            test_id = self.collection.index(test)
            self.node2pending[node].append(test_id)
        for node in self.nodes:
            node.send_runtest_some(self.node2pending[node])
        self.pending = []

        for node in self.nodes:
            node.shutdown()
