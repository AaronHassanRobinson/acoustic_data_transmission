### Format:
Data is sent in the format: 
[preamble][start bit][byte_1][stop bit]...[start bit][byte_x][stop bit]

For simulation, data is packed in the format:
[preamble][data]


## limitations:
This protocol is limited by no error handling, half duplex implemtation, and no crypt