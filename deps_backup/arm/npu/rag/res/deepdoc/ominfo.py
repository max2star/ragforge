#
#  Copyright 2024 The InfiniFlow Authors. All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
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