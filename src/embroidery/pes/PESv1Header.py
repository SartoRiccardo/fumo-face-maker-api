from dataclasses import dataclass


@dataclass
class PESv1Header:
    pec_section_offset: int
    large_hoop: bool
    use_existing_design_area: bool
    segment_block_count: int

    def to_bytes(self) -> bytes:
        return (
            b"#PES0001" +
            self.pec_section_offset.to_bytes(4, "little") +
            int(self.large_hoop).to_bytes(2, "little") +
            int(self.use_existing_design_area).to_bytes(2, "little") +
            self.segment_block_count.to_bytes(2, "little")
        )

    @classmethod
    def length(cls):
        return 4 + 4 + 4 + 2 + 2 + 2
