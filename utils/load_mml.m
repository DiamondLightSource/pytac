function load_mml(ringmode)

    fprintf('Loading data for ring mode %s\n', ringmode);
    dir = fileparts(mfilename('fullpath'));
    cd(dir);

    loaded_mode = getfamilydata('OperationalMode');

    if ~strcmp(loaded_mode, ringmode)
        fprintf('MML ring mode %s loaded, not %s\n', loaded_mode, ringmode);
        fprintf('Exiting.\n');
        return;
    end

    switch2sim;

    % load directly into the ap SQL database
    dir = fileparts(mfilename('fullpath'));
    cd(dir);
    elements_file = fullfile(dir, '..', 'data', ringmode, 'elements.csv');
    f_elements = fopen(elements_file, 'wt', 'n', 'utf-8');
    fprintf(f_elements, 'id,name,type,length,cell\n');
    devices_file = fullfile(dir, '..', 'data', ringmode, 'devices.csv');
    f_devices = fopen(devices_file, 'w');
    fprintf(f_devices, 'id,field,get_pv,set_pv,enable_pv,enable_value\n');
    families_file = fullfile(dir, '..', 'data', ringmode, 'families.csv');
    f_families = fopen(families_file, 'w');
    fprintf(f_families, 'id,family\n');

    global THERING;
    ao = getao();

    % The individual BPM PVs are not stored in middlelayer.
    BPMS = get_bpm_pvs(ao);

    % Map from AT types to types in the accelerator object (ao).
    global TYPE_MAP;
    keys = {'QUAD', 'SEXT', 'VSTR', 'HSTR', 'BEND'};
    values = {'QUAD_', 'SEXT_', 'VCM', 'HCM', 'BB'};
    TYPE_MAP = containers.Map(keys, values);

    used_elements = containers.Map();
    renamed_indexes = containers.Map('KeyType', 'int32', 'ValueType', 'int32');

    s = 0;
    new_index = 0;

    for old_index = 1:length(THERING)
        at_elm = THERING{old_index};
        s = s + at_elm.Length;
        if not(strcmp(at_elm.FamName, 'HSTR') || strcmp(at_elm.FamName, 'VSTR'))
            new_index = new_index + 1;
            insertelement(new_index, old_index, at_elm, s, ringmode);
        else
            fprintf(f_families, '%i,%s\n', new_index, at_elm.FamName);
        end

        type = gettype(at_elm);
        if used_elements.isKey(type)
            used_elements(type) = used_elements(type) + 1;
        else
            used_elements(type) = 1;
        end
        pvs = getpvs(ao, at_elm);
        insertpvs(new_index, pvs);

        renamed_indexes(old_index) = new_index;
    end

    % The following families  and do not have their
    % own elements.  We insert their PVs separately.
    insertextrapvs('SQUAD', 'a1');
    insertextrapvs('BBVMXS', 'db0');
    insertextrapvs('BBVMXL', 'db0');

    % DCCT not in THERING.
    dcct = struct ('FamName', 'DCCT', 'Length', 0);
    new_index = new_index + 1;
    old_index = old_index + 1;
    insertelement(new_index, old_index, dcct, 0, ringmode);
    s = pv_struct('I', 'SR-DI-DCCT-01:SIGNAL', '', '', '');
    insertpvs(new_index, {s});

    renamed_indexes(old_index) = new_index;
    fclose(f_elements);
    fclose(f_devices);
    fclose(f_families);

    fprintf('Loaded %d mml elements into %d pytac elements.\n', old_index, new_index);

    % finally, load unit conversion data
    load_unitconv(ringmode, renamed_indexes);

    function type = gettype(elm)
        if isfield(elm, 'Class')
            type = elm.Class;
        elseif isfield(elm, 'FamName')
                type = elm.FamName;
        else
            type = '';
        end
    end


    function insertpvs(index, pvs)
        if size(pvs) == 0
            return;
        end
        for i = 1:size(pvs, 2)
            %fprintf('%s: %d\n', deblank(pvs{i}.pv), size(deblank(pvs{i}.pv), 2));
            fprintf(f_devices, '%d,%s,%s,%s,%s,%s\n', index, pvs{i}.field, deblank(pvs{i}.get_pv), deblank(pvs{i}.set_pv), deblank(pvs{i}.enable_pv), pvs{i}.enable_value);
        end
    end


    % Construct BPM PVs from MML indices
    function bpms = get_bpm_pvs(ao)
        nbpms = size(ao.BPMx.DeviceList, 1);
        bpms = cell(nbpms);
        for i = 1:nbpms
            ncell = ao.BPMx.DeviceList(i,1);
            index = ao.BPMx.DeviceList(i,2);
            if mod(ncell, 1) ~= 0
                % Indices of .5 correspond to SRnnS-DI-EBPM-nn.
                ncell = fix(ncell);
                bpms{i} = sprintf('SR%02dS-DI-EBPM-%02d', ncell, index);
            else
                bpms{i} = sprintf('SR%02dC-DI-EBPM-%02d', ncell, index);
            end
        end
    end


    function pvs = getpvs(ao, elm)
        type = gettype(elm);

        if any(ismember(type, TYPE_MAP.keys))
            if strcmp(type, 'QUAD')
                field = 'b1';
            elseif strcmp(type, 'SEXT')
                field = 'b2';
            elseif strcmp(type, 'VSTR')
                field = 'a0';
            elseif strcmp(type, 'HSTR') || strcmp(type, 'BEND')
                field = 'b0';
            end
            % MML is inconsistent about whether the family for the bends
            % is BEND or BB.
            if strcmp(type, 'BEND') && isfield(ao, 'BEND')
                family = 'BEND';
            else
                family = TYPE_MAP(type);
            end
            index = used_elements(type);

            get_pv = char(ao.(family).Monitor.ChannelNames(index, :));
            set_pv = char(ao.(family).Setpoint.ChannelNames(index, :));
            pvs = pv_struct(field, get_pv, set_pv, '', '');
            pvs = {pvs};
        elseif strcmp(type, 'BPM')
            index = used_elements(type);
            enable_pv = strcat(BPMS{index}, ':CF:ENABLED_S');
            get_x_pv = strcat(BPMS{index}, ':SA:X');
            x_pv = pv_struct('x', get_x_pv, '', enable_pv, '1');
            get_y_pv = strcat(BPMS{index}, ':SA:Y');
            y_pv = pv_struct('y', get_y_pv, '', enable_pv, '1');
            pvs = {x_pv, y_pv};
        elseif strcmp(type, 'RF')
            gfpv = ao.(type).Monitor.ChannelNames;
            sfpv = ao.(type).Setpoint.ChannelNames;
            f_pvs = pv_struct('f', gfpv, sfpv, '', '');
            % voltage?
            pvs = {f_pvs};
        else
            pvs = {};
        end

    end

    function insertextrapvs(family, field)
        elms = getfamilydata(family);
        if ~isempty(elms)
            for i = 1:length(elms.AT.ATIndex)
                get_pv = elms.Monitor.ChannelNames(i,:);
                set_pv = elms.Setpoint.ChannelNames(i,:);
                pvs = pv_struct(field, set_pv, get_pv, '', '');
                insertpvs(renamed_indexes(elms.AT.ATIndex(i)), {pvs});
            end
        end
    end

    function s = pv_struct(field, get_pv, set_pv, enable_pv, enable_value)
        s = struct('field', field, 'get_pv', get_pv, 'set_pv', set_pv, 'enable_pv', enable_pv, 'enable_value', enable_value);
    end

    function insertelement(i, old_i, at_elm, s, ringmode)
        type = gettype(at_elm);
        fprintf(f_families, '%i,%s\n', i, at_elm.FamName);
        cell = getcell(old_i, at_elm.FamName);

        % Elements with additional PVs require an extra group added.
        % The ATIndex array lists the original indexes, so we need
        % old_index to correctly check if this element was a member
        % of the group.
        extra_groups = {'SQUAD'};
        for j = 1:length(extra_groups)
            group = extra_groups{j};
            elms = getfamilydata(group);
            if ~isempty(elms) && ismember(old_i, elms.AT.ATIndex)
                fprintf(f_families, '%i,%s\n', i, group);
            end
        end

        fprintf(f_elements, '%d,%d,%s,%f,%d\n', i, i, type, at_elm.Length, cell);
    end

    function cell = getcell(old_i, family)
        cell = '';
        familydata = getfamilydata(family);
        if ~isempty(familydata) && isfield(familydata, 'AT')
            family_index = familydata.AT.ATIndex == old_i;
            cell = floor(familydata.DeviceList(family_index, 1));
        end
    end

end
