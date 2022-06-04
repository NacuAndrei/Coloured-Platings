# CandyCrush-alike problem using KR algorithms

Given a matrix of colours that define some pieces, determine the minium cost solution for eliminating all pieces.
A piece can be eliminated if it has at least k platings of the same colour.
A blank space will be represented as '#' and it can be filled in 2 ways : 
 a) the piece above falls in its place
 b) if no piece is above, one from the right will take its place
 
- the cost of a move is 1+(N-K)/N.
- N is the total number of same coloured platings as the eliminated piece 
- K is the total number of platings removed by the move.

Example:
aaa
abbb
cccc
aaaa

#### (empty)
aaaa
abbb
aaaa
Movement cost: 1.

####
####
####
bbb#
Movement cost: 1.

####
####
####
####
Movement cost: 1.

Total: 3 moves with a total cost of 3. 

Used A-star algorithm + BF / DF for eficiency comparison.
-2nd year of university
