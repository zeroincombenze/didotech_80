cmodule=$(basename $PWD)
[[ $cmodule != "didotech_80" ]] && echo "Invalid environment!" && exit 1
[[ -z $1 || $1 != "restore" ]] && action="replace" || action="restore"
if [[ $action == "restore" ]]; then
    tkn_src="False"
    tkn_tgt="True"
else
    tkn_src="True"
    tkn_tgt="False"
fi
root=$(readlink -f $PWD/..)
for path in ./*; do
    [[ ! -d $path ]] && continue
    module=$(basename $path)
    grep -qE "installable.*: *False" $path/__openerp__.py && continue
    echo -en "."
    dispath=$(find $root -type d -not -path "*/$cmodule/*" -name $module)
    [[ -z $dispath ]] && continue
    echo -en "\r"
    manifest="$dispath/__openerp__.py"
    echo $manifest
    sed -E "s/(installable.*: *)$tkn_src/\1$tkn_tgt/" -i $manifest
    grep -EH "installable.*:" $manifest
done
echo ""
