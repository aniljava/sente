BLACK = -1
WHITE = 1
EMPTY = 0


# Todo : Group statistics
# Todo : Scoring
# Todo : Statistics on moves


class Board:
    
    def __init__(self, size = 19):
        self.size = size
        self.clear()
    
    def clear(self):
        self.stones = [[0 for x in range(self.size)] for y in range(self.size)] 
        self.groups = [[0 for x in range(self.size)] for y in range(self.size)] 
        self.liberties = [[0 for x in range(self.size)] for y in range(self.size)] 
        
        self.group_id = 1
        
        self.black_captures = []
        self.white_captures = []
        
        self.last_capture = None
        self.last_move = None
        
        self.group_index = {}
        self.sequence = []
        
    
    def is_legal(self, color, pos):
        x,y = pos
        opposite_color = color * -1
        
        # false if already occupied
        if self.stones[x][y] != EMPTY:
            return False, 'NOT EMPTY' + str(pos)

        
        # Check KO
        # false if marked for ko, superko
        if pos == self.last_capture:
            
            # Check if not snap back
            lx,ly = self.last_move
            last_move_group = self.groups[lx][ly]
            
            other_stones_group = [self.groups[sx][sy] for sx,sy in self.neighbours(self.last_move)]
            if not last_move_group in other_stones_group:
                # Existance of Ko
                return False, 'KO'
        
        
        for n in self.neighbours(pos):
            nx, ny = n
            
            # true if space around
            if self.stones[nx][ny] == EMPTY:
                return True, 'EMPTY AROUND'
            # true if same color groups around with liberty > 1
            elif self.stones[nx][ny] == color:
                if self.liberties[nx][ny] > 1:
                    return True, 'Same color lib + 1'
            
            # true if opposite color groups around with liberty == 0
            elif self.stones[nx][ny] == opposite_color:
                if self.liberties[nx][ny] == 1:
                    return True, 'Opposite color lib = 1'
        
        # False, probably atari
        return False, 'ATARI' + str(pos)


    def move(self, color, pos, check=True):
        
        if check:
            legal , message = self.is_legal(color,pos)
            if not legal:
                message += ' Move : {}'.format(len(self.sequence))
                
                raise Exception(message)
                return False
        
        x, y = pos
        
        print 'PLAYING', pos
        
        opposite_color = color * -1
        self.stones[x][y] = color
        
        self.sequence.append((color, x,y,))
        
        neighbours = self.neighbours(pos)
        
        all_spaces = True
        for n in neighbours:
            nx, ny = n
            if self.stones[nx][ny] != EMPTY:
                all_spaces = False
        
        if all_spaces :
            self.group_id += 1
            self.group_index[self.group_id] = [pos]
            self.liberties[x][y] = len(neighbours)
            self.groups[x][y] = self.group_id
            return
            
        
        # Add to group and merge groups if needed
        
        group_id = -1
        for n in neighbours:
            nx,ny = n
            
            if self.stones[nx][ny] == color:
                stone_group = self.groups[nx][ny]
                if group_id == -1:
                    group_id = stone_group
                    self.groups[x][y] = group_id
                    self.group_index[group_id].append(pos)
                    
                else:
                    stone_group = self.groups[nx][ny]
                    if stone_group != group_id:
                        # different group
                        for stone in self.group_index[stone_group]:
                            sx, sy = stone
                            # add to new group
                            self.group_index[group_id].append(stone)
                            self.groups[sx][sy] = group_id
                        del self.group_index[stone_group]
                         
        
        # No group fround, possibly in opposite + space or capture
        if group_id == -1:
            self.group_id += 1            
            self.group_index[self.group_id] = [pos]
            self.groups[x][y] = self.group_id
            group_id = self.group_id
        
        liberty_update_set = set([group_id])
        
        
        captures = []
        
        for n in neighbours:
            nx,ny = n
            if self.stones[nx][ny] == opposite_color:
                group = self.groups[nx][ny]
                stones = self.group_index[group]
                stones = [s for s in stones]
                for stone in stones:
                    print stone
                    sx, sy = stone
                    self.liberties[sx][sy] -= 1
                                    
                    if self.liberties[sx][sy] == 0:
                        self.stones[sx][sy] = EMPTY  # Remove stone
                        self.groups[sx][sy] = 0
                        self.group_index[group].remove(stone)
                        captures.append(stone)
                        
                        # mark sorrounding enemy groups for liberty update
                        for sg in self.neighbours(stone):
                            sgx, sgy = sg
                            if self.stones[sgx][sgy] == color:
                                liberty_update_set.add(self.groups[sgx][sgy])
        
        # Calculate liberties for all in queues
        for group_id in liberty_update_set:
            self.update_liberty(group_id)
        
        if len(captures) == 1:
            self.last_capture = captures[0]
        else:
            self.last_capture = None
        
        self.last_move = pos
        if len(captures) > 0:
            if color == BLACK:
                self.black_captures.extend(captures)
            else:
                self.white_captures.extend(captures)
        
        # TODO: Update capture record, keep a ko marker if length == 1
        
        
        # place stone
        # assign new group_id
        # for all opposite_group_around: update liberties
        # for all opposite_group_around: remove if liberty is zero
        # for all self_group around: assign new groupid
        # for all self_group around: update liberty
        # mark for ko and superko
        
    def update_liberty(self, group_id):
        if group_id == 0:
            return

        space_set = set()
        for stone in self.group_index[group_id]:
            sx, sy = stone
            spaces = [pos for pos in self.neighbours(stone) if self.stones[pos[0]][pos[1]] == EMPTY]
            space_set.update(spaces)
        
        
        liberty = len(space_set)
        for stone in self.group_index[group_id]:
            sx, sy = stone
            self.liberties[sx][sy] = liberty
            
        
    # Profiling gave this a better performance
    def neighbours(self, pos):
        x, y = pos
        
        MAX = self.size - 1
        
        if x == 0:
            if y == 0:
                return [(1, 0), (0, 1)]
            elif y == MAX:
                return [(0, MAX - 1), (1, MAX)]
            else:
                return [(1, y), (0, y - 1), (0, y + 1) ]
        elif x == MAX:
            if y == 0:
                return [(MAX - 1, 0), (MAX, 1)]
            elif y == MAX:
                return [(MAX - 1, MAX), (MAX, MAX - 1)]
            else:
                return [(MAX - 1, y), (MAX, y - 1), (MAX, y + 1) ]
        else:
            if y == 0:
                return [(x - 1, 0), (x + 1, 0), (x, 1) ]
            elif y == MAX:
                return [(x - 1, MAX), (x + 1, MAX), (x, MAX - 1) ]
            else:
                return [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1) ]
            
    
    
    
    def __str__(self):
        lines = []
        for y in range(self.size):
            rows = []
            for x in range(self.size):
                
                liberty = str(self.liberties[x][y]).zfill(2)
                
                cell = ''
                if self.stones[x][y] == BLACK:
                    cell += ' B{} '.format(liberty)
                elif self.stones[x][y] == WHITE:
                    cell += ' W{} '.format(liberty)
                else:
                    cell += ' .   '
                rows.append(cell) 
            rows = ''.join(rows)
            lines.append(rows)
        lines.reverse()
        
        return '\n'.join(lines)