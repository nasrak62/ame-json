
class ProgressiveAssembler {
    constructor() {
        this.final_data = {};
        this.path_data_mapper = {};
    }

    _decode_value(value) {
        return JSON.parse(value);
    }

    _insert_value(data, path, value) {
        let data_value = data;
        for (let i = 0; i < path.length; i++) {
            const path_part = path[i];
            if (!(path_part in data_value)) {
                throw new Error(`Bad path: ${path}`);
            }
            if (i === path.length - 1) {
                data_value[path_part] = value;
                continue;
            }
            data_value = data_value[path_part];
        }
    }

    _get_first_computed_key(keys) {
        for (const key of keys) {
            if (key.startsWith('$')) {
                return key;
            }
        }
        return null;
    }

    _get_current_path(keys) {
        const key = this._get_first_computed_key(keys);
        if (key === null) {
            return [];
        }
        const path_data = this.path_data_mapper[key];
        if (path_data === undefined) {
            return [];
        }
        return path_data.path;
    }

    update_data(object_value) {
        const keys = Object.keys(object_value);
        const current_path = this._get_current_path(keys);

        for (const [key, value] of Object.entries(object_value)) {
            if (key.startsWith('$')) {
                if (!(key in this.path_data_mapper)) {
                    console.error(`key was not in pending update data: ${key}`);
                    continue;
                }
                const path_data = this.path_data_mapper[key];
                if (!path_data) {
                    console.error(`can't find path for key: ${key}`);
                    continue;
                }
                this._insert_value(this.final_data, path_data.path, value);
                continue;
            }

            if (typeof value === 'string' && value.startsWith('$')) {
                const path = [...current_path, key];
                this.path_data_mapper[value] = { value: value, path: path };
            }
            this.final_data[key] = value;
        }
        return this.final_data;
    }

    assemble(chunk) {
        const object_value = this._decode_value(chunk);
        const is_finished = object_value.completed_stream === true;
        
        if (is_finished){
            delete object_value.completed_stream;
        }

        const updated_data = this.update_data(object_value);

        return {
            is_finished,
            data: updated_data
        };
    }
}
