from test_sdkbase import TestSdk
from ragflow import RAGFlow
import pytest
from common import API_KEY, HOST_ADDRESS
from api.contants import NAME_LENGTH_LIMIT


class TestDataset(TestSdk):
    """
    This class contains a suite of tests for the dataset management functionality within the RAGFlow system.
    It ensures that the following functionalities as expected:
        1. create a kb
        2. list the kb
        3. get the detail info according to the kb id
        4. update the kb
        5. delete the kb
    """
    # -----------------------create_dataset---------------------------------
    def test_create_dataset_with_success(self):
        """
        Test the creation of a new dataset with success.
        """
        ragflow = RAGFlow(API_KEY, HOST_ADDRESS)
        # create a kb
        res = ragflow.create_dataset("kb1")
        assert res['code'] == 0 and res['message'] == 'success'

    def test_create_dataset_with_empty_name(self):
        """
        Test the creation of a new dataset with an empty name.
        """
        ragflow = RAGFlow(API_KEY, HOST_ADDRESS)
        res = ragflow.create_dataset("")
        assert res['message'] == 'Empty dataset name' and res['code'] == 102

    def test_create_dataset_with_name_exceeding_limit(self):
        """
        Test the creation of a new dataset with the length of name exceeding the limit.
        """
        name = "k" * NAME_LENGTH_LIMIT + "b"
        ragflow = RAGFlow(API_KEY, HOST_ADDRESS)
        res = ragflow.create_dataset(name)
        assert (res['message'] == f"Dataset name: {name} with length {len(name)} exceeds {NAME_LENGTH_LIMIT}!"
                and res['code'] == 102)

    def test_create_dataset_name_with_space_in_the_middle(self):
        """
        Test the creation of a new dataset whose name has space in the middle.
        """
        name = "k b"
        ragflow = RAGFlow(API_KEY, HOST_ADDRESS)
        res = ragflow.create_dataset(name)
        assert (res['code'] == 0 and res['message'] == 'success')

    def test_create_dataset_name_with_space_in_the_head(self):
        """
        Test the creation of a new dataset whose name has space in the head.
        """
        name = " kb"
        ragflow = RAGFlow(API_KEY, HOST_ADDRESS)
        res = ragflow.create_dataset(name)
        assert (res['code'] == 0 and res['message'] == 'success')

    def test_create_dataset_name_with_space_in_the_tail(self):
        """
        Test the creation of a new dataset whose name has space in the tail.
        """
        name = "kb "
        ragflow = RAGFlow(API_KEY, HOST_ADDRESS)
        res = ragflow.create_dataset(name)
        assert (res['code'] == 0 and res['message'] == 'success')

    def test_create_dataset_name_with_space_in_the_head_and_tail_and_length_exceed_limit(self):
        """
        Test the creation of a new dataset whose name has space in the head and tail,
        and the length of the name exceeds the limit.
        """
        name = " " + "k" * NAME_LENGTH_LIMIT + " "
        ragflow = RAGFlow(API_KEY, HOST_ADDRESS)
        res = ragflow.create_dataset(name)
        assert (res['code'] == 0 and res['message'] == 'success')

    def test_create_dataset_with_two_same_name(self):
        """
        Test the creation of two new datasets with the same name.
        """
        ragflow = RAGFlow(API_KEY, HOST_ADDRESS)
        res = ragflow.create_dataset("kb")
        assert (res['code'] == 0 and res['message'] == 'success')
        res = ragflow.create_dataset("kb")
        assert (res['code'] == 0 and res['message'] == 'success')

    def test_create_dataset_with_only_space_in_the_name(self):
        """
        Test the creation of a dataset whose name only has space.
        """
        ragflow = RAGFlow(API_KEY, HOST_ADDRESS)
        res = ragflow.create_dataset(" ")
        assert (res['code'] == 0 and res['message'] == 'success')

    def test_create_dataset_with_space_number_exceeding_limit(self):
        """
        Test the creation of a dataset with a name that only has space exceeds the allowed limit.
        """
        ragflow = RAGFlow(API_KEY, HOST_ADDRESS)
        name = " " * NAME_LENGTH_LIMIT
        res = ragflow.create_dataset(name)
        assert (res['code'] == 0 and res['message'] == 'success')

    def test_create_dataset_with_name_having_return(self):
        """
        Test the creation of a dataset with a name that has return symbol.
        """
        ragflow = RAGFlow(API_KEY, HOST_ADDRESS)
        name = "kb\n"
        res = ragflow.create_dataset(name)
        assert (res['code'] == 0 and res['message'] == 'success')

    def test_create_dataset_with_name_having_the_null_character(self):
        """
        Test the creation of a dataset with a name that has the null character.
        """
        ragflow = RAGFlow(API_KEY, HOST_ADDRESS)
        name = "kb\0"
        res = ragflow.create_dataset(name)
        assert (res['code'] == 0 and res['message'] == 'success')

    # -----------------------list_dataset---------------------------------
    def test_list_dataset_success(self):
        """
        Test listing datasets with a successful outcome.
        """
        ragflow = RAGFlow(API_KEY, HOST_ADDRESS)
        # Call the list_datasets method
        response = ragflow.list_dataset()

        code, datasets = response

        assert code == 200

    def test_list_dataset_with_checking_size_and_name(self):
        """
        Test listing datasets and verify the size and names of the datasets.
        """
        datasets_to_create = ["dataset1", "dataset2", "dataset3"]
        ragflow = RAGFlow(API_KEY, HOST_ADDRESS)
        created_response = [ragflow.create_dataset(name) for name in datasets_to_create]

        real_name_to_create = set()
        for response in created_response:
            assert 'data' in response, "Response is missing 'data' key"
            dataset_name = response['data']['dataset_name']
            real_name_to_create.add(dataset_name)

        status_code, listed_data = ragflow.list_dataset(0, 3)
        listed_data = listed_data['data']

        listed_names = {d['name'] for d in listed_data}
        assert listed_names == real_name_to_create
        assert status_code == 200
        assert len(listed_data) == len(datasets_to_create)

    def test_list_dataset_with_getting_empty_result(self):
        """
        Test listing datasets that should be empty.
        """
        ragflow = RAGFlow(API_KEY, HOST_ADDRESS)
        datasets_to_create = []
        created_response = [ragflow.create_dataset(name) for name in datasets_to_create]

        real_name_to_create = set()
        for response in created_response:
            assert 'data' in response, "Response is missing 'data' key"
            dataset_name = response['data']['dataset_name']
            real_name_to_create.add(dataset_name)

        status_code, listed_data = ragflow.list_dataset(0, 0)
        listed_data = listed_data['data']

        listed_names = {d['name'] for d in listed_data}
        assert listed_names == real_name_to_create
        assert status_code == 200
        assert len(listed_data) == 0

    def test_list_dataset_with_creating_100_knowledge_bases(self):
        """
        Test listing 100 datasets and verify the size and names of these datasets.
        """
        ragflow = RAGFlow(API_KEY, HOST_ADDRESS)
        datasets_to_create = ["dataset1"] * 100
        created_response = [ragflow.create_dataset(name) for name in datasets_to_create]

        real_name_to_create = set()
        for response in created_response:
            assert 'data' in response, "Response is missing 'data' key"
            dataset_name = response['data']['dataset_name']
            real_name_to_create.add(dataset_name)

        status_code, listed_data = ragflow.list_dataset(0, 100)
        listed_data = listed_data['data']

        listed_names = {d['name'] for d in listed_data}
        assert listed_names == real_name_to_create
        assert status_code == 200
        assert len(listed_data) == 100

    def test_list_dataset_with_showing_one_dataset(self):
        """
        Test listing one dataset and verify the size of the dataset.
        """
        ragflow = RAGFlow(API_KEY, HOST_ADDRESS)
        response = ragflow.list_dataset(0, 1)
        code, response = response
        datasets = response['data']
        assert len(datasets) == 1

    def test_list_dataset_failure(self):
        """
        Test listing datasets with IndexError.
        """
        ragflow = RAGFlow(API_KEY, HOST_ADDRESS)
        response = ragflow.list_dataset(-1, -1)
        _, res = response
        assert "IndexError" in res['message']

    def test_list_dataset_for_empty_datasets(self):
        """
        Test listing datasets when the datasets are empty.
        """
        ragflow = RAGFlow(API_KEY, HOST_ADDRESS)
        response = ragflow.list_dataset()
        code, response = response
        datasets = response['data']
        assert len(datasets) == 0

    # TODO: have to set the limitation of the number of datasets

    # -----------------------delete_dataset---------------------------------
    def test_delete_one_dataset_with_success(self):
        """
        Test deleting a dataset with success.
        """
        # get the real name of the created dataset
        ragflow = RAGFlow(API_KEY, HOST_ADDRESS)
        res = ragflow.create_dataset("kb0")
        real_dataset_name = res['data']['dataset_name']
        # delete this dataset
        result = ragflow.delete_dataset(real_dataset_name)
        assert result["success"] is True

    def test_delete_dataset_with_not_existing_dataset(self):
        """
        Test deleting a dataset that does not exist with failure.
        """
        ragflow = RAGFlow(API_KEY, HOST_ADDRESS)
        res = ragflow.delete_dataset("weird_dataset")
        assert res["success"] is False

    def test_delete_dataset_with_creating_100_datasets_and_deleting_100_datasets(self):
        """
        Test deleting a dataset when creating 100 datasets and deleting 100 datasets.
        """
        # create 100 datasets
        ragflow = RAGFlow(API_KEY, HOST_ADDRESS)
        datasets_to_create = ["dataset1"] * 100
        created_response = [ragflow.create_dataset(name) for name in datasets_to_create]

        real_name_to_create = set()
        for response in created_response:
            assert 'data' in response, "Response is missing 'data' key"
            dataset_name = response['data']['dataset_name']
            real_name_to_create.add(dataset_name)

        for name in real_name_to_create:
            res = ragflow.delete_dataset(name)
            assert res["success"] is True

    def test_delete_dataset_with_space_in_the_middle_of_the_name(self):
        """
        Test deleting a dataset when its name has space in the middle.
        """
        ragflow = RAGFlow(API_KEY, HOST_ADDRESS)
        res = ragflow.delete_dataset("k b")
        print(res)
        assert res["success"] is True

    def test_delete_dataset_with_space_in_the_head_of_the_name(self):
        """
        Test deleting a dataset when its name has space in the head.
        """
        ragflow = RAGFlow(API_KEY, HOST_ADDRESS)
        res = ragflow.delete_dataset(" kb")
        assert res["success"] is False

    def test_delete_dataset_with_space_in_the_tail_of_the_name(self):
        """
        Test deleting a dataset when its name has space in the tail.
        """
        ragflow = RAGFlow(API_KEY, HOST_ADDRESS)
        res = ragflow.delete_dataset("kb ")
        assert res["success"] is False

    def test_delete_dataset_with_only_space_in_the_name(self):
        """
        Test deleting a dataset when its name only has space.
        """
        ragflow = RAGFlow(API_KEY, HOST_ADDRESS)
        res = ragflow.delete_dataset(" ")
        assert res["success"] is False

    def test_delete_dataset_with_only_exceeding_limit_space_in_the_name(self):
        """
        Test deleting a dataset when its name only has space and the number of it exceeds the limit.
        """
        ragflow = RAGFlow(API_KEY, HOST_ADDRESS)
        name = " " * (NAME_LENGTH_LIMIT + 1)
        res = ragflow.delete_dataset(name)
        assert res["success"] is False

    def test_delete_dataset_with_name_with_space_in_the_head_and_tail_and_length_exceed_limit(self):
        """
        Test deleting a dataset whose name has space in the head and tail,
        and the length of the name exceeds the limit.
        """
        ragflow = RAGFlow(API_KEY, HOST_ADDRESS)
        name = " " + "k" * NAME_LENGTH_LIMIT + " "
        res = ragflow.delete_dataset(name)
        assert res["success"] is False

    # ---------------------------------mix the different methods--------------------
    def test_create_and_delete_dataset_together(self):
        """
        Test creating 1 dataset, and then deleting 1 dataset.
        Test creating 10 datasets, and then deleting 10 datasets.
        """
        # create 1 dataset
        ragflow = RAGFlow(API_KEY, HOST_ADDRESS)
        res = ragflow.create_dataset("ddd")
        assert res['code'] == 0 and res['message'] == 'success'

        # delete 1 dataset
        res = ragflow.delete_dataset("ddd")
        assert res["success"] is True

        # create 10 datasets
        datasets_to_create = ["dataset1"] * 10
        created_response = [ragflow.create_dataset(name) for name in datasets_to_create]

        real_name_to_create = set()
        for response in created_response:
            assert 'data' in response, "Response is missing 'data' key"
            dataset_name = response['data']['dataset_name']
            real_name_to_create.add(dataset_name)

        # delete 10 datasets
        for name in real_name_to_create:
            res = ragflow.delete_dataset(name)
            assert res["success"] is True

