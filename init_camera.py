class Camera is
# 使用状态模式，实现内部状态转移，与转移前的附加操作
    field state: state
    
    constructor Camera() is
        this.state = new Done(this)

    method changeState(State state) is
        this.state = state

# 类似Java接口
abstract class State is
    protected field player: AudioPlayer

    constructor State(player) is
        this.player = player

    abstract method action()

# 接口具体实现
class INIT extends State is
    method action() is
        if roi_not_selected:
            camera.changeState(new INIT(camera)) # 重建一个新的本状态，重新运行
        if can_go_pdaf:
            # go to pdaf
            camera.changeState(new DAF_TAF(camera))
        else:
            camera.changeState(new PREPARE(camera))

class DAF_TAF extends State is
    method action() is
        if low_confidence:
            # go to CDAF
            camera.changeState(new INIT(camera))
        else:
            # start moving
            camera.changeState(new DAF_MOV(camera))

class DAF_MOV extends State is
    method action() is
        if hunting or moving_timeout or low_confidence or source_invalid_timeout:
            # go to CDAF
            camera.changeState(new INIT(camera))
        elif keep_moving:
            camera.changeState(new DAF_MOV(camera)) # 重复新建该状态
        else:
            # the pre-conditions before converged to FS
            camera.changeState(new DAF_FS(camera))

class DAF_FS extends State is
    method action() is
        if timeout:
            # go to CDAF
            camera.changeState(new INIT(camera))
        elif keep_finesearch:
            camera.changeState(new DAF_MOV(camera)) # 重复新建该状态
        else:
            # 1. Find peak 2. Fit PL 3. go to tar pos due to timeout
            camera.changeState(new MOVETOBEST(camera))

class MOVETOBEST extends State is
    method action() is
        if auto_mode:
            camera.changeState(new DONE(camera))
        elif continuous_mode:
            camera.changeState(new MONITOR(camera))

class DONE extends State is
    method action() is
        # start AF
        camera.changeState(new INIT(camera))

class MONITOR extends State is
    method action() is
        if no_scene_change:
            camera.changeState(new MONITOR(camera)) # 重新转移回自身
        elif scene_change_occur:
            camera.changeState(new INIT(camera))
    
class PREPARE extends State is
    method action() is
        if not_ready:
            camera.changeState(new PREPARE(camera)) # 重新转移回自身
        elif reday_to_search:
            camera.changeState(new SEEK(camera))

class SEEK extends State is
    method action() is
        if high_confidence:
            camera.changeState(new INIT(camera))
        elif need_to_change_direction:
            camera.changeState(new DIRCHG(camera))
        elif peak_is_found or search_finished and peak_not_found:
            camera.changeState(new MOVETOBEST(camera))

class DIRCHG extends State is
    method action() is
        if needs_to_change_direction:
            camera.changeState(new SEEK(camera))
