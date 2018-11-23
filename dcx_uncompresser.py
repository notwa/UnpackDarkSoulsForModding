import struct
import zlib
import sys
import os

def consume_byte(content, offset, byte, length=1):
    """Consume length bytes from content, starting at offset. If they
     are not all byte, raises a ValueError.
    """
    
    for i in xrange(0, length):
        if content[offset + i] != byte:
            raise ValueError("Expected byte '" + byte.encode("hex") + "' at offset " +\
                    hex(offset + i) + " but received byte '" +\
                    content[offset + i].encode("hex") + "'.")
    return offset + length
    
def appears_dcx(content):
    """Checks if the magic bytes at the start of content indicate that it
    is a .dcx file.
    """
    return content[0:4] == "DCX\x00"
   
def uncompress_dcx_content(content):
    """Decompress the file content from a .dcx file. Returns the uncompressed
    content. Raising ValueError if the header does not match the required format.
    """
    master_offset = 0
    master_offset = consume_byte(content, master_offset, 'D', 1)
    master_offset = consume_byte(content, master_offset, 'C', 1)
    master_offset = consume_byte(content, master_offset, 'X', 1)
    master_offset = consume_byte(content, master_offset, '\x00', 1)
    
    (req_1,) = struct.unpack_from("<I", content, offset=master_offset)
    master_offset += struct.calcsize("<I")
    (req_2, req_3, req_4) = struct.unpack_from(">III", content, offset=master_offset)
    master_offset += struct.calcsize(">III")
    if req_1 != 0x100:
        raise ValueError("Expected DCX header int 0x100, but received " + hex(req_1))
    if req_2 != 0x18:
        raise ValueError("Expected DCX header int 0x18, but received " + hex(req_2))
    if req_3 != 0x24:
        raise ValueError("Expected DCX header int 0x24, but received " + hex(req_3))
    if req_4 != 0x24:
        raise ValueError("Expected DCX header int 0x24, but received " + hex(req_4))
    
    (header_length,) = struct.unpack_from(">I", content, offset=master_offset)
    master_offset += struct.calcsize(">I")
    
    master_offset = consume_byte(content, master_offset, 'D', 1)
    master_offset = consume_byte(content, master_offset, 'C', 1)
    master_offset = consume_byte(content, master_offset, 'S', 1)
    master_offset = consume_byte(content, master_offset, '\x00', 1)
    
    (uncomp_size, comp_size) = struct.unpack_from(">II", content, offset=master_offset)
    master_offset += struct.calcsize(">II")
    
    master_offset = consume_byte(content, master_offset, 'D', 1)
    master_offset = consume_byte(content, master_offset, 'C', 1)
    master_offset = consume_byte(content, master_offset, 'P', 1)
    master_offset = consume_byte(content, master_offset, '\x00', 1)

    master_offset = consume_byte(content, master_offset, 'E', 1)
    master_offset = consume_byte(content, master_offset, 'D', 1)
    master_offset = consume_byte(content, master_offset, 'G', 1)
    master_offset = consume_byte(content, master_offset, 'E', 1)

    # Skip the portion of the header whose meaning is unknown.
    master_offset += 0x18
    master_offset = consume_byte(content, master_offset, 'D', 1)
    master_offset = consume_byte(content, master_offset, 'C', 1)
    master_offset = consume_byte(content, master_offset, 'A', 1)
    master_offset = consume_byte(content, master_offset, '\x00', 1)

    (comp_header_length,) = struct.unpack_from(">I", content, offset=master_offset)
    master_offset += struct.calcsize(">I")
    comp_start = master_offset + comp_header_length - 8

    master_offset = consume_byte(content, master_offset, 'E', 1)
    master_offset = consume_byte(content, master_offset, 'g', 1)
    master_offset = consume_byte(content, master_offset, 'd', 1)
    master_offset = consume_byte(content, master_offset, 'T', 1)

    (req_1, req_2, req_3, req_4) = struct.unpack_from(">IIII", content, offset=master_offset)
    master_offset += struct.calcsize(">IIII")
    assert req_1 == 0x00010100, req_1
    assert req_2 == 0x00000024, req_2
    assert req_3 == 0x00000010, req_3
    assert req_4 == 0x00010000, req_4

    # TODO:
    master_offset += struct.calcsize(">IIII")
    max_decomp_size = 0x10000

    decomp = ""

    segment_count = (comp_header_length - 0x2C) / 0x10
    for seg in xrange(segment_count):
        (zero, seg_offset, seg_comp_size, seg_comped) = struct.unpack_from(">IIII", content, offset=master_offset)
        master_offset += struct.calcsize(">IIII")

        assert zero == 0, zero
        assert seg_comped == 0 or seg_comped == 1, seg_comped

        seg_offset += comp_start
        if seg_comped:
            decomp_obj = zlib.decompressobj(-zlib.MAX_WBITS)
            decomp += decomp_obj.decompress(content[seg_offset:seg_offset + seg_comp_size], max_decomp_size)
        else:
            decomp += content[seg_offset:seg_offset + seg_comp_size]

    assert len(decomp) == uncomp_size
    return decomp
    
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "Usage: " + str(sys.argv[0]) + " <DCX File>"
    else:
        filename = sys.argv[1]
        if filename[-4:] == ".dcx":
            uncomp_filename = filename[:-4]
        else:
            uncomp_filename = filename + ".undcx"
        with open(filename, "rb") as f, open(uncomp_filename, "wb") as g:
            file_content = f.read()
            g.write(uncompress_dcx_content(file_content))
            g.close()
            
    

    
    
     

