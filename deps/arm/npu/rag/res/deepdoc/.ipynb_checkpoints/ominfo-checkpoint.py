import aclruntime
import argparse

def main(args):
    model_dir = args.input
    device_id = 0
    
    options = aclruntime.session_options()
    session = aclruntime.InferenceSession(model_dir, device_id, options)
    
    # print model input info
    for i in range(len(session.get_inputs())):
        print(f"inputs {i} name: {session.get_inputs()[i].name}")
        print(f"inputs {i} shape: {session.get_inputs()[i].shape}")
        print(f"inputs {i} data type: {session.get_inputs()[i].datatype}")
        print(f"inputs {i} bytes shape: {session.get_inputs()[i].realsize}")
    
    # print model output info
    for i in range(len(session.get_outputs())):
        print(f"outputs {i} name: {session.get_outputs()[i].name}")
        print(f"outputs {i} shape: {session.get_outputs()[i].shape}")
        print(f"outputs {i} data type: {session.get_outputs()[i].datatype}")
        print(f"outputs {i} bytes shape: {session.get_outputs()[i].realsize}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', '-i', help="model dir", required=True)
    args = parser.parse_args()
    main(args)