#include <iostream>
#include <vector>
#include <string>
#include <array>
#include <stdexcept>
#include <algorithm>
#include <numeric>

using namespace std;

// ---------------------------------------------------------------------------
// Constants & Enums
// ---------------------------------------------------------------------------
enum Corners { URF=0, UFL=1, ULB=2, UBR=3, DFR=4, DLF=5, DBL=6, DRB=7 };
enum Edges { UR=0, UF=1, UL=2, UB=3, DR=4, DF=5, DL=6, DB=7, FR=8, FL=9, BL=10, BR=11 };
enum Faces { U_FACE=0, R_FACE=1, F_FACE=2, D_FACE=3, L_FACE=4, B_FACE=5 };

const int CORNER_FACELET[8][3] = {
    {8, 9, 20}, {6, 18, 38}, {0, 36, 47}, {2, 45, 11},
    {29, 26, 15}, {27, 44, 24}, {33, 53, 42}, {35, 17, 51}
};

const int EDGE_FACELET[12][2] = {
    {5, 10}, {7, 19}, {3, 37}, {1, 46},
    {32, 16}, {28, 25}, {30, 43}, {34, 52},
    {23, 12}, {21, 41}, {48, 39}, {50, 14}
};

const int CORNER_COLOR[8][3] = {
    {U_FACE, R_FACE, F_FACE}, {U_FACE, F_FACE, L_FACE}, {U_FACE, L_FACE, B_FACE}, {U_FACE, B_FACE, R_FACE},
    {D_FACE, F_FACE, R_FACE}, {D_FACE, L_FACE, F_FACE}, {D_FACE, B_FACE, L_FACE}, {D_FACE, R_FACE, B_FACE}
};

const int EDGE_COLOR[12][2] = {
    {U_FACE, R_FACE}, {U_FACE, F_FACE}, {U_FACE, L_FACE}, {U_FACE, B_FACE},
    {D_FACE, R_FACE}, {D_FACE, F_FACE}, {D_FACE, L_FACE}, {D_FACE, B_FACE},
    {F_FACE, R_FACE}, {F_FACE, L_FACE}, {B_FACE, L_FACE}, {B_FACE, R_FACE}
};

int PHASE2_MOVES[] = {0, 1, 2, 9, 10, 11, 4, 13, 7, 16};

// ---------------------------------------------------------------------------
// Math Utilities
// ---------------------------------------------------------------------------
int comb(int n, int k) {
    if (k < 0 || k > n) return 0;
    if (k == 0 || k == n) return 1;
    long long res = 1;
    for (int i = 1; i <= k; ++i) {
        res = res * (n - i + 1) / i;
    }
    return (int)res;
}

// ---------------------------------------------------------------------------
// CubieCube
// ---------------------------------------------------------------------------
struct CubieCube {
    std::array<int, 8> cp;
    std::array<int, 8> co;
    std::array<int, 12> ep;
    std::array<int, 12> eo;

    CubieCube() {
        for (int i=0; i<8; ++i) { cp[i] = i; co[i] = 0; }
        for (int i=0; i<12; ++i) { ep[i] = i; eo[i] = 0; }
    }

    CubieCube(const std::array<int, 8>& cp_, const std::array<int, 8>& co_,
              const std::array<int, 12>& ep_, const std::array<int, 12>& eo_)
        : cp(cp_), co(co_), ep(ep_), eo(eo_) {}

    CubieCube multiply(const CubieCube& other) const {
        CubieCube res;
        for (int i=0; i<8; ++i) {
            res.cp[i] = cp[other.cp[i]];
            res.co[i] = (co[other.cp[i]] + other.co[i]) % 3;
        }
        for (int i=0; i<12; ++i) {
            res.ep[i] = ep[other.ep[i]];
            res.eo[i] = (eo[other.ep[i]] + other.eo[i]) % 2;
        }
        return res;
    }

    bool is_solved() const {
        for (int i=0; i<8; ++i) if (cp[i] != i || co[i] != 0) return false;
        for (int i=0; i<12; ++i) if (ep[i] != i || eo[i] != 0) return false;
        return true;
    }
};

CubieCube MOVE_CUBE[18];
string MOVE_NAMES[18] = {
    "U", "U2", "U'",
    "R", "R2", "R'",
    "F", "F2", "F'",
    "D", "D2", "D'",
    "L", "L2", "L'",
    "B", "B2", "B'"
};

void init_base_moves() {
    CubieCube moveU({UBR, URF, UFL, ULB, DFR, DLF, DBL, DRB},
                    {0, 0, 0, 0, 0, 0, 0, 0},
                    {UB, UR, UF, UL, DR, DF, DL, DB, FR, FL, BL, BR},
                    {0,0,0,0,0,0,0,0,0,0,0,0});
                    
    CubieCube moveR({DFR, UFL, ULB, URF, DRB, DLF, DBL, UBR},
                    {2, 0, 0, 1, 1, 0, 0, 2},
                    {FR, UF, UL, UB, BR, DF, DL, DB, DR, FL, BL, UR},
                    {0,0,0,0,0,0,0,0,0,0,0,0});

    CubieCube moveF({UFL, DLF, ULB, UBR, URF, DFR, DBL, DRB},
                    {1, 2, 0, 0, 2, 1, 0, 0},
                    {UR, FL, UL, UB, DR, FR, DL, DB, UF, DF, BL, BR},
                    {0, 1, 0, 0, 0, 1, 0, 0, 1, 1, 0, 0});

    CubieCube moveD({URF, UFL, ULB, UBR, DLF, DBL, DRB, DFR},
                    {0,0,0,0,0,0,0,0},
                    {UR, UF, UL, UB, DF, DL, DB, DR, FR, FL, BL, BR},
                    {0,0,0,0,0,0,0,0,0,0,0,0});

    CubieCube moveL({URF, ULB, DBL, UBR, DFR, UFL, DLF, DRB},
                    {0, 1, 2, 0, 0, 2, 1, 0},
                    {UR, UF, BL, UB, DR, DF, FL, DB, FR, UL, DL, BR},
                    {0,0,0,0,0,0,0,0,0,0,0,0});

    CubieCube moveB({URF, UFL, UBR, DRB, DFR, DLF, ULB, DBL},
                    {0, 0, 1, 2, 0, 0, 2, 1},
                    {UR, UF, UL, BR, DR, DF, DL, BL, FR, FL, UB, DB},
                    {0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 1});

    CubieCube bases[6] = {moveU, moveR, moveF, moveD, moveL, moveB};
    for(int i=0; i<6; ++i) {
        CubieCube x1 = bases[i];
        CubieCube x2 = x1.multiply(x1);
        CubieCube x3 = x2.multiply(x1);
        MOVE_CUBE[i*3] = x1;
        MOVE_CUBE[i*3+1] = x2;
        MOVE_CUBE[i*3+2] = x3;
    }
}

CubieCube from_face_string(const string& s) {
    if (s.length() != 54) throw runtime_error("Face string must be 54 characters");
    int face_map[256];
    fill_n(face_map, 256, -1);
    face_map[(unsigned char)s[4]] = U_FACE;
    face_map[(unsigned char)s[13]] = R_FACE;
    face_map[(unsigned char)s[22]] = F_FACE;
    face_map[(unsigned char)s[31]] = D_FACE;
    face_map[(unsigned char)s[40]] = L_FACE;
    face_map[(unsigned char)s[49]] = B_FACE;
    
    int mapped = 0;
    for(int i=0;i<256;++i) if(face_map[i] != -1) mapped++;
    if(mapped != 6) throw runtime_error("Invalid center facelets");

    vector<int> facelets(54);
    for(int i=0; i<54; ++i) {
        int f = face_map[(unsigned char)s[i]];
        if(f == -1) throw runtime_error("Invalid facelet character");
        facelets[i] = f;
    }

    CubieCube c;
    for(int i=0; i<8; ++i) {
        int f0 = facelets[CORNER_FACELET[i][0]];
        int f1 = facelets[CORNER_FACELET[i][1]];
        int f2 = facelets[CORNER_FACELET[i][2]];
        bool found = false;
        for(int ori=0; ori<3; ++ori) {
            int r0=f0, r1=f1, r2=f2;
            if(ori==1) { r0=f1; r1=f2; r2=f0; }
            else if(ori==2) { r0=f2; r1=f0; r2=f1; }
            if(r0 != U_FACE && r0 != D_FACE) continue;
            for(int j=0; j<8; ++j) {
                if(r0 == CORNER_COLOR[j][0] && r1 == CORNER_COLOR[j][1] && r2 == CORNER_COLOR[j][2]) {
                    c.cp[i] = j;
                    c.co[i] = ori;
                    found = true;
                    break;
                }
            }
            if(found) break;
        }
        if(!found) throw runtime_error("Cannot identify corner");
    }

    for(int i=0; i<12; ++i) {
        int f0 = facelets[EDGE_FACELET[i][0]];
        int f1 = facelets[EDGE_FACELET[i][1]];
        bool found = false;
        for(int ori=0; ori<2; ++ori) {
            int r0 = (ori==0) ? f0 : f1;
            int r1 = (ori==0) ? f1 : f0;
            for(int j=0; j<12; ++j) {
                if(r0 == EDGE_COLOR[j][0] && r1 == EDGE_COLOR[j][1]) {
                    c.ep[i] = j;
                    c.eo[i] = ori;
                    found = true;
                    break;
                }
            }
            if(found) break;
        }
        if(!found) throw runtime_error("Cannot identify edge");
    }
    return c;
}

// ---------------------------------------------------------------------------
// Coordinates
// ---------------------------------------------------------------------------
int corner_orientation_coord(const array<int, 8>& co) {
    int val = 0;
    for(int i=0; i<7; ++i) val = val * 3 + co[i];
    return val;
}
array<int, 8> corner_orientation_from_coord(int val) {
    array<int, 8> co;
    int parity = 0;
    for(int i=6; i>=0; --i) {
        co[i] = val % 3;
        parity += co[i];
        val /= 3;
    }
    co[7] = (3 - parity % 3) % 3;
    return co;
}

int edge_orientation_coord(const array<int, 12>& eo) {
    int val = 0;
    for(int i=0; i<11; ++i) val = val * 2 + eo[i];
    return val;
}
array<int, 12> edge_orientation_from_coord(int val) {
    array<int, 12> eo;
    int parity = 0;
    for(int i=10; i>=0; --i) {
        eo[i] = val % 2;
        parity += eo[i];
        val /= 2;
    }
    eo[11] = parity % 2;
    return eo;
}

int ud_slice_coord(const array<int, 12>& ep) {
    int val = 0;
    int k = 3;
    for(int i=11; i>=0; --i) {
        if(ep[i] >= 8) {
            val += comb(i, k+1);
            k--;
        }
    }
    return 494 - val;
}
array<int, 12> ud_slice_from_coord(int val) {
    val = 494 - val;
    vector<int> slice_pos;
    int k = 3;
    for(int i=11; i>=0; --i) {
        if(k < 0) break;
        int c = comb(i, k+1);
        if(val >= c) {
            val -= c;
            slice_pos.push_back(i);
            k--;
        }
    }
    array<int, 12> ep;
    fill(ep.begin(), ep.end(), -1);
    int slice_edge = 8, non_slice_edge = 0;
    for(int i=0; i<12; ++i) {
        if(find(slice_pos.begin(), slice_pos.end(), i) != slice_pos.end()) {
            ep[i] = slice_edge++;
        } else {
            ep[i] = non_slice_edge++;
        }
    }
    return ep;
}

int perm_to_index(const vector<int>& perm) {
    int n = perm.size();
    int index = 0;
    for(int i=0; i<n; ++i) {
        int count = 0;
        for(int j=i+1; j<n; ++j) {
            if(perm[j] < perm[i]) count++;
        }
        index = index * (n - i) + count;
    }
    return index;
}

vector<int> index_to_perm(int index, int n) {
    vector<int> lehmer(n);
    for(int i=n-1; i>=0; --i) {
        lehmer[i] = index % (n - i);
        index /= (n - i);
    }
    vector<int> available(n);
    iota(available.begin(), available.end(), 0);
    vector<int> perm(n);
    for(int i=0; i<n; ++i) {
        perm[i] = available[lehmer[i]];
        available.erase(available.begin() + lehmer[i]);
    }
    return perm;
}

int corner_perm_coord(const array<int, 8>& cp) {
    return perm_to_index(vector<int>(cp.begin(), cp.end()));
}
array<int, 8> corner_perm_from_coord(int val) {
    vector<int> p = index_to_perm(val, 8);
    array<int, 8> cp;
    copy(p.begin(), p.end(), cp.begin());
    return cp;
}

int ud_edge_perm_coord(const array<int, 12>& ep) {
    return perm_to_index(vector<int>(ep.begin(), ep.begin()+8));
}
array<int, 12> ud_edge_perm_from_coord(int val) {
    vector<int> p = index_to_perm(val, 8);
    array<int, 12> ep;
    for(int i=0; i<8; ++i) ep[i] = p[i];
    for(int i=8; i<12; ++i) ep[i] = i;
    return ep;
}

int ud_slice_perm_coord(const array<int, 12>& ep) {
    vector<int> sub(4);
    for(int i=0; i<4; ++i) sub[i] = ep[i+8] - 8;
    return perm_to_index(sub);
}
array<int, 12> ud_slice_perm_from_coord(int val) {
    vector<int> p = index_to_perm(val, 4);
    array<int, 12> ep;
    for(int i=0; i<8; ++i) ep[i] = i;
    for(int i=0; i<4; ++i) ep[i+8] = p[i] + 8;
    return ep;
}

// ---------------------------------------------------------------------------
// Tables
// ---------------------------------------------------------------------------
uint16_t co_move[2187][18];
uint16_t eo_move[2048][18];
uint16_t uds_move[495][18];
uint16_t cp_move[40320][18];
uint16_t ep_move[40320][18];
uint16_t usp_move[24][18];

uint8_t co_uds_prune[2187 * 495];
uint8_t eo_uds_prune[2048 * 495];
uint8_t cp_usp_prune[40320 * 24];
uint8_t ep_usp_prune[40320 * 24];

void build_move_tables() {
    for(int i=0; i<2187; ++i) {
        auto co = corner_orientation_from_coord(i);
        CubieCube c; c.co = co;
        for(int m=0; m<18; ++m) {
            co_move[i][m] = corner_orientation_coord(c.multiply(MOVE_CUBE[m]).co);
        }
    }
    for(int i=0; i<2048; ++i) {
        auto eo = edge_orientation_from_coord(i);
        CubieCube c; c.eo = eo;
        for(int m=0; m<18; ++m) {
            eo_move[i][m] = edge_orientation_coord(c.multiply(MOVE_CUBE[m]).eo);
        }
    }
    for(int i=0; i<495; ++i) {
        auto ep = ud_slice_from_coord(i);
        CubieCube c; c.ep = ep;
        for(int m=0; m<18; ++m) {
            uds_move[i][m] = ud_slice_coord(c.multiply(MOVE_CUBE[m]).ep);
        }
    }
    for(int i=0; i<40320; ++i) {
        auto cp = corner_perm_from_coord(i);
        CubieCube c; c.cp = cp;
        for(int m=0; m<18; ++m) {
            cp_move[i][m] = corner_perm_coord(c.multiply(MOVE_CUBE[m]).cp);
        }
    }
    for(int i=0; i<40320; ++i) {
        auto ep = ud_edge_perm_from_coord(i);
        CubieCube c; c.ep = ep;
        for(int m=0; m<18; ++m) {
            ep_move[i][m] = ud_edge_perm_coord(c.multiply(MOVE_CUBE[m]).ep);
        }
    }
    for(int i=0; i<24; ++i) {
        auto ep = ud_slice_perm_from_coord(i);
        CubieCube c; c.ep = ep;
        for(int m=0; m<18; ++m) {
            usp_move[i][m] = ud_slice_perm_coord(c.multiply(MOVE_CUBE[m]).ep);
        }
    }
}

void build_pruning_table(uint8_t* table, int size1, int size2, uint16_t move1[][18], uint16_t move2[][18], const vector<int>& moves) {
    int total = size1 * size2;
    fill(table, table + total, 255);
    table[0] = 0;
    int done = 1;
    int depth = 0;
    while(true) {
        int added = 0;
        for(int i=0; i<total; ++i) {
            if(table[i] != depth) continue;
            int c1 = i / size2;
            int c2 = i % size2;
            for(int m : moves) {
                int n1 = move1[c1][m];
                int n2 = move2[c2][m];
                int ni = n1 * size2 + n2;
                if(table[ni] == 255) {
                    table[ni] = depth + 1;
                    done++;
                    added++;
                }
            }
        }
        if(added == 0) break;
        depth++;
    }
}

void build_all_pruning_tables() {
    vector<int> moves18(18); iota(moves18.begin(), moves18.end(), 0);
    vector<int> moves10(PHASE2_MOVES, PHASE2_MOVES + 10);
    
    build_pruning_table(co_uds_prune, 2187, 495, co_move, uds_move, moves18);
    build_pruning_table(eo_uds_prune, 2048, 495, eo_move, uds_move, moves18);
    build_pruning_table(cp_usp_prune, 40320, 24, cp_move, usp_move, moves10);
    build_pruning_table(ep_usp_prune, 40320, 24, ep_move, usp_move, moves10);
}

// ---------------------------------------------------------------------------
// Validation
// ---------------------------------------------------------------------------
int perm_parity(const std::array<int, 8>& p) {
    int n = 8;
    vector<bool> vis(n, false);
    int parity = 0;
    for(int i=0; i<n; ++i) {
        if(vis[i]) continue;
        int j = i;
        int cycle = 0;
        while(!vis[j]) {
            vis[j] = true;
            j = p[j];
            cycle++;
        }
        if(cycle > 1) parity ^= (cycle + 1) % 2;
    }
    return parity;
}

int perm_parity(const std::array<int, 12>& p) {
    int n = 12;
    vector<bool> vis(n, false);
    int parity = 0;
    for(int i=0; i<n; ++i) {
        if(vis[i]) continue;
        int j = i;
        int cycle = 0;
        while(!vis[j]) {
            vis[j] = true;
            j = p[j];
            cycle++;
        }
        if(cycle > 1) parity ^= (cycle + 1) % 2;
    }
    return parity;
}

void validate_cube(const CubieCube& cube) {
    int co_sum = 0; for(int i=0; i<8; ++i) co_sum += cube.co[i];
    if(co_sum % 3 != 0) throw runtime_error("Invalid corner orientation parity");
    
    int eo_sum = 0; for(int i=0; i<12; ++i) eo_sum += cube.eo[i];
    if(eo_sum % 2 != 0) throw runtime_error("Invalid edge orientation parity");

    auto cp_sort = cube.cp; sort(cp_sort.begin(), cp_sort.end());
    for(int i=0; i<8; ++i) if(cp_sort[i] != i) throw runtime_error("Invalid corner permutation");

    auto ep_sort = cube.ep; sort(ep_sort.begin(), ep_sort.end());
    for(int i=0; i<12; ++i) if(ep_sort[i] != i) throw runtime_error("Invalid edge permutation");

    if(perm_parity(cube.cp) != perm_parity(cube.ep)) throw runtime_error("Permutation parity mismatch");
}

// ---------------------------------------------------------------------------
// Solver
// ---------------------------------------------------------------------------
bool can_follow(int move, int last_move) {
    if(last_move < 0) return true;
    int face = move / 3;
    int last_face = last_move / 3;
    if(face == last_face) return false;
    int face_sum = face + last_face;
    if(face_sum == 3 || face_sum == 5 || face_sum == 7) {
        if(face > last_face) return false;
    }
    return true;
}

class Solver {
public:
    bool phase1_search(int co, int eo, int uds, int depth, int max_depth, int last_move, vector<int>& sol) {
        int h = max(co_uds_prune[co * 495 + uds], eo_uds_prune[eo * 495 + uds]);
        if(depth + h > max_depth) return false;
        if(co == 0 && eo == 0 && uds == 0) return true;
        for(int m=0; m<18; ++m) {
            if(!can_follow(m, last_move)) continue;
            sol.push_back(m);
            if(phase1_search(co_move[co][m], eo_move[eo][m], uds_move[uds][m], depth+1, max_depth, m, sol)) return true;
            sol.pop_back();
        }
        return false;
    }

    bool phase2_search(int cp, int ep, int usp, int depth, int max_depth, int last_move, vector<int>& sol) {
        int h = max(cp_usp_prune[cp * 24 + usp], ep_usp_prune[ep * 24 + usp]);
        if(depth + h > max_depth) return false;
        if(cp == 0 && ep == 0 && usp == 0) return true;
        for(int m : PHASE2_MOVES) {
            if(!can_follow(m, last_move)) continue;
            sol.push_back(m);
            if(phase2_search(cp_move[cp][m], ep_move[ep][m], usp_move[usp][m], depth+1, max_depth, m, sol)) return true;
            sol.pop_back();
        }
        return false;
    }

    vector<int> solve(CubieCube cube) {
        if(cube.is_solved()) return {};

        int co = corner_orientation_coord(cube.co);
        int eo = edge_orientation_coord(cube.eo);
        int uds = ud_slice_coord(cube.ep);

        vector<int> best_sol;
        for(int p1_max=0; p1_max<=20; ++p1_max) {
            vector<int> p1_sol;
            if(!phase1_search(co, eo, uds, 0, p1_max, -1, p1_sol)) continue;

            CubieCube g1 = cube;
            for(int m : p1_sol) g1 = g1.multiply(MOVE_CUBE[m]);

            int cp = corner_perm_coord(g1.cp);
            int ep = ud_edge_perm_coord(g1.ep);
            int usp = ud_slice_perm_coord(g1.ep);

            int max_total = best_sol.empty() ? 22 : best_sol.size() - 1;
            int p2_max = max_total - p1_sol.size();
            if(p2_max < 0) break;

            vector<int> total;
            if(cp == 0 && ep == 0 && usp == 0) {
                total = p1_sol;
            } else {
                vector<int> p2_sol;
                if(!phase2_search(cp, ep, usp, 0, p2_max, -1, p2_sol)) continue;
                total = p1_sol;
                total.insert(total.end(), p2_sol.begin(), p2_sol.end());
            }

            if(best_sol.empty() || total.size() < best_sol.size()) {
                best_sol = total;
                if(best_sol.size() <= p1_sol.size() + 1) break;
            }
        }
        
        if(best_sol.empty()) throw runtime_error("No solution found");
        return best_sol;
    }
};

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

static bool tables_initialized = false;

void init_kociemba_solver() {
    if (tables_initialized) return;
    init_base_moves();
    build_move_tables();
    build_all_pruning_tables();
    tables_initialized = true;
}

std::vector<std::string> solve_rubiks_cube(const std::string& s) {
    if (s.length() != 54) {
        throw std::runtime_error("Face string must be exactly 54 characters");
    }
    init_kociemba_solver();
    
    CubieCube c = from_face_string(s);
    validate_cube(c);
    
    Solver solver;
    std::vector<int> move_indices = solver.solve(c);
    
    std::vector<std::string> move_names;
    for(int m : move_indices) {
        move_names.push_back(MOVE_NAMES[m]);
    }
    return move_names;
}
