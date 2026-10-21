class SequenceDataset:
    """Build a Dataset and custom `collate_fn` for variable-length sequences that pads examples, returns masks and labels/metadata, and supports device transfer."""

    def __init__(self, *args, **kwargs):
        raise NotImplementedError("TODO: implement PT-06")
